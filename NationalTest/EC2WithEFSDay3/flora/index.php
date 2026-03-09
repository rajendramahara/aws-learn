<!DOCTYPE html>
<html>
<head>
    <title>Flora Gallery</title>
</head>
<body>
    <h1 style="text-align:center;">Flora Gallery</h1>
    <?php
    // Get all images from /efs/flora
    $files = glob('/efs/flora/*.{jpg,png,jpeg,gif}', GLOB_BRACE);

    foreach ($files as $file) {
        // Convert /efs/flora/image.jpg to /flora/image.jpg
        $webPath = str_replace('/efs', '', $file);
        echo "<img src='{$webPath}' width='200' style='margin:10px;'>";
    }
    ?>
</body>
</html>


<!-- sudo nano /etc/httpd/conf/httpd.conf
<Directory "/var/www/html">
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory> -->
