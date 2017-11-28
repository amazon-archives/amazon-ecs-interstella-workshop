#!/bin/bash
#cat indexstart > index.html
echo '<!DOCTYPE html>
<html>
<head>
  <title>Lab Instructions</title>
    <meta name="description" content="Interstella instructions" />

    </head>

    <body>
    <textarea theme="cerulean" style="display:none;">
' > index.html
cat readme.md >> index.html

echo "
## Credits
Markdown rendering by [Strapdown.js]('http://strapdownjs.com/')

</textarea>
<script src='js/strapdown/strapdown.js'></script>
</body>
</html>" >> index.html
#zip -r bundle tests/ code/ hints/ -x "*.DS_Store"
aws s3 sync . s3://www.interstella.trade/workshop3/ --acl public-read --exclude ".DS_Store"
