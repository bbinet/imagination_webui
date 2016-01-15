<%!
    import time
%>
<html>
<head>
  <title>imagination_webui</title>
</head>
<body>
  <h1 class="title">Import photos from your Flickr photosets</h1>
  % if request.authenticated_userid:
    <h2>Flickr user: ${request.authenticated_userid} [<a href="${request.route_url('flickr_logout')}">Logout from Flickr</a>]</h2>
    <ul>
    % for s in flickr.photosets.getList(user_id=request.authenticated_userid, format='parsed-json')['photosets']['photoset']:
      <li>
      ${s['title']['_content']} (${s['photos']} photos) [last updated ${time.strftime('%d/%m/%Y %H:%M', time.gmtime(float(s['date_update'])))}]:
        <a href="${request.route_url('flickr_import_setid', set_id=s['id'])}">Import</a>
      </li>
    % endfor
    </ul>
  % else:
    <h2>Not authenticated [<a href="${request.route_url('flickr_login')}">Login through Flickr</a>]</h2>
  % endif
</body>
</html>
