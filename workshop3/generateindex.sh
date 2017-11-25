#!/bin/bash

#cat indexstart > index.html
echo '<!DOCTYPE html>
<html>
<head>
  <title>Lab Instructions</title>
    <meta name="description" content="Interstella instructions" />

    </head>

    <body>
    <textarea theme="spacelab" style="display:none;">
' > index.html
cat readme.md >> index.html

echo "
## Credits
Markdown rendering by [Strapdown.js]('http://strapdownjs.com/')

</textarea>
<script src='http://strapdownjs.com/v/0.2/strapdown.js'></script>
</body>
</html>" >> index.html

aws s3 cp index.html s3://www.interstella.trade/workshop3/index.html --acl public-read
