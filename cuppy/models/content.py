import datetime
from pyramid.threadlocal import get_current_request

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import DateTime

from sqlalchemy.types import Boolean
from sqlalchemy.types import Enum
from sqlalchemy.orm import relationship, relation
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import backref

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

from .meta import Base
from .meta import DBSession
from ..utils.util import title_to_slug


class SiteRoot(Base):
    __tablename__ = 'site_root'
    id = Column(Integer, primary_key=True)
    # Use for meta title, defaults to content title
    meta_title = Column(Unicode(250))
    # Description is what appears in search result, defaults to autogenerated content.
    description = Column(UnicodeText)
    # Slug is the url of the content
    slug = Column(String(2000))
    position = Column(Integer)
    parent_id = Column(Integer, ForeignKey('site_root.id'))
    children = relationship("SiteRoot",
                        order_by="SiteRoot.position",
                        collection_class=ordering_list('position'),
                        #cascade="all, delete,delete-orphan",
                        backref=backref("parent", remote_side=id)
                    )
    type = Column(String(50), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity':'site_root',
        'polymorphic_on':type
    }

    def __init__(self, 
        meta_title: str = None, 
        description: str = None,
        slug: str = None, 
        parent_id: int = None):

        self.meta_title = meta_title
        self.description = description
        self.slug = slug
        self.parent_id = parent_id
                

    def keys(self, parent_id):
        """The keys here are the slugs. Given a parent id 
        return the slugs of the children to
        this parent. If the parent id is None then return the
         slugs of all objects with no parent"""
        if parent_id:
            doc = DBSession.query(SiteRoot).get(parent_id)
            return [child.slug for child in doc.children]
        return self.slugs()
    
    def slugs(self):
        "Returns slugs of all objects with no parent"
        return [i.slug for i in DBSession.query(SiteRoot).filter(SiteRoot.parent_id==None).all()]

    def values(self):
        return self.children

    def get_slug(self):
        "Child classes should override this to provide a better url generation"
        return self.slug

    def generate_unique_slug(self, parent_id):
        if parent_id:
            parent = SiteRoot.get_by_id(parent_id)
            slug = parent.get_slug()
            return title_to_slug(self.meta_title, self.keys(parent_id),slug)
        return title_to_slug(self.meta_title,self.keys(parent_id))
    
    def change_slug(self, slug):
        "Change slug of an existing object to a new slug"
        return title_to_slug(slug, self.keys(self.parent_id))

    @classmethod
    def get_by_id(cls,id):
        return DBSession.query(cls).filter_by(id=id).first()
    
    @classmethod
    def get_by_slug(cls,slug):
        
        return DBSession.query(cls).filter_by(slug=slug).first()


class Tag(Base):
    
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_by_name(cls, name):
        tag = DBSession.query(cls).filter(cls.name==name).first()
        return tag

    @classmethod
    def get_by_id(cls, id_):
        q= DBSession.query(cls).filter(cls.id == id_)
        return q.first()


class ContentTags(Base):

    __tablename__ = 'content_tags'
    tag_id = Column('tag_id', ForeignKey('tags.id'), primary_key=True, index=True)
    content_id = Column('content_id', ForeignKey('contents.id'), primary_key=True, index=True)
    tag = relation(Tag, backref=backref("content_tags", cascade="all"), lazy="joined")
    position = Column(Integer, nullable=False)
    name = association_proxy('tag','name')

    @classmethod
    def _tag_find_or_create(cls, name: str):
        with DBSession.no_autoflush:
            tag = DBSession.query(Tag).filter(Tag.name==name).first()
        if tag is None:
            tag = Tag(name=name)
        return cls(tag=tag)


class Content(SiteRoot):

    """ This is the base class for creation of custom content type"""

    __tablename__ = "contents"
    id= Column(Integer, ForeignKey('site_root.id'), primary_key=True)
    #Content title
    title = Column(Unicode(255))
    status = Column(Enum("draft","published", name="status"), default='published')
    creation_date = Column(DateTime)
    modification_date = Column(DateTime)
    in_menu = Column(Boolean(name="in_menu"), default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="contents")
    
    _tags = relation(
        ContentTags,
        backref=backref("content"),
        lazy="joined",
        order_by=[ContentTags.position],
        collection_class=ordering_list("position"),
        cascade="all, delete-orphan",
    )
    #: Tags assigned to the content object (list of str)
    tags = association_proxy(
        "_tags", "name", creator=ContentTags._tag_find_or_create
    )
    

    __mapper_args__ = {
        'polymorphic_identity':'content'
    }

    def __init__(self, 
        title: str = None, 
        status: str = "published",
        creation_date: datetime.datetime = None,
        modification_date: datetime.datetime = None,
        in_menu: bool = True,
        user: 'User' = None,
        tags = None,
        **kwargs):

        super().__init__(**kwargs)

        self.title= title
        self.status = status
        self.creation_date = creation_date
        self.modification_date = modification_date
        self.in_menu = in_menu
        self.user = user
        self.tags = tags or []
    
    @classmethod
    def published_with_correct_date(self):
        if self.published and self.creation_date <= datetime.datetime.now():
            return True
    
    @classmethod
    def get_query(cls, with_selectinload=True):
        query = DBSession.query(cls)
        if with_selectinload:
            query = query.options(selectinload('tags'), selectinload('users'))
        return query
    
    @classmethod
    def get_by_tagname(cls, tag_name, with_selectinload=True):
        query = cls.get_query(with_selectinload)
        return query.filter(Content.tags.any(name=tag_name)).all()
   

class Document(Content):
    " Document adds body to content"
    __tablename__ = 'documents'
    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    body = Column(UnicodeText)
    
    __mapper_args__ = {
        'polymorphic_identity':'document'
    }

    def __init__(self, body='', **kwargs):

        super().__init__(**kwargs)

        self.body = body


    def get_slug(self):

        "Build slugs from parents"

        slug = super(Document,self).get_slug()
        if self.parent is not None:
            return "%s/%s" % (self.parent.slug, slug)
        return slug

    def set_slug(self, new_slug):
        "Changes the document slug"
        
        available_slugs = self.keys(self.parent_id)
        # Remove this particular document's slug from available slug
        # to avoid throwing error if new slug is same as old slug
        available_slugs.pop(self.slug)
        
        # New_slug must not have '/' character
        new_slug = new_slug.split('/')[-1]
        # Check if new_slug exist
        if new_slug in available_slugs:
            raise ValueError("There's already a document with this slug, you can either change"  
            "the slug or change the parent of this document and try again")
        
        if self.parent:
            new_slug = "%s/%s".format(self.parent.slug, new_slug)
        self.slug = new_slug
        

    def set_parent(self, new_parent):

        "Changes the document parent and the slug if necessary"

        # Avoid a circle
        parent = new_parent
        while parent is not None:
            if parent.id == self.id:
                raise AttributeError(" You can't set a page or it's child as parent")
            parent = parent.parent

        self.parent = new_parent
        try:
            self.set_slug(self.slug)
        except ValueError:
            #We have to now generate a new slug
            self.generate_unique_slug(self.parent_id)

    @property
    def add_route_name(self):
        return "add_doc"
    
    @property
    def edit_route_name(self):
        return "edit_doc"
    
    @property
    def delete_route_name(self):
        return "delete_doc"

    @property
    def verbose_name(self):
        return "Document"


class File(Content):
    " A file is an image,video etc. It adds filename to content"
    __tablename__ = 'files'
    id = Column(Integer, ForeignKey('contents.id'),primary_key=True)
    filename = Column(Unicode(255))
    


    