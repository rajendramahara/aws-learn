<!DOCTYPE html>
<html>
<head>
    <title>Fauna Gallery</title>
</head>
<body>
    <h1 style="text-align:center;">Fauna Gallery</h1>
    <?php
    // Get all images from /efs/fauna
    $files = glob('/efs/fauna/*.{jpg,png,jpeg,gif}', GLOB_BRACE);

    foreach ($files as $file) {
        $webPath = str_replace('/efs', '', $file);
        echo "<img src='{$webPath}' width='200' style='margin:10px;'>";
    }
    ?>
</body>
</html>
