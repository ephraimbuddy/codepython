<!DOCTYPE html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="pyramid web application">
    <meta name="author" content="Pylons Project">
    <link rel="shortcut icon" href="${request.static_url('cuppy:static/pyramid-16x16.png')}">

    <title>Cookiecutter Starter project for the Pyramid Web Framework</title>
    
    
  </head>

  <body>

    <div class="starter-template">
      <div class="container">
        <div class="row">
          <div class="col-md-2">
            <img class="logo img-responsive" src="${request.static_url('cuppy:static/pyramid.png') }" alt="pyramid web framework">
          </div>
          <div class="col-md-10">
            ${ next.body() }
          </div>
        </div>
        <div class="row">
          <div class="links">
            <ul>
              <li><i class="glyphicon glyphicon-cog icon-muted"></i><a href="https://github.com/Pylons/pyramid">Github Project</a></li>
              <li><i class="glyphicon glyphicon-globe icon-muted"></i><a href="https://webchat.freenode.net/?channels=pyramid">IRC Channel</a></li>
              <li><i class="glyphicon glyphicon-home icon-muted"></i><a href="https://pylonsproject.org">Pylons Project</a></li>
            </ul>
          </div>
        </div>
        <div class="row">
          <div class="copyright">
            Copyright &copy; Pylons Project
          </div>
        </div>
      </div>
    </div>


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//code.jquery.com/jquery-1.12.4.min.js" integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ=" crossorigin="anonymous"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
  </body>
</html>

