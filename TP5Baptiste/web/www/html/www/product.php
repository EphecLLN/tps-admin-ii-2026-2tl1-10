<html>
<head>
    <title>Catalogue WoodyToys</title>
    <style>
        table, th, td {
            padding: 10px;
            border: 1px solid black;
            border-collapse: collapse;
        }
    </style>
</head>
<body>
    <h1>Catalogue WoodyToys - Groupe l1-10</h1>
    <?php
    $dbname = 'woodytoys';
    $dbuser = 'root';
    $dbpass = 'mypass';
    // ATTENTION : Vérifiez bien cette IP avec 'docker inspect mariadbtest'
    $dbhost = 'db-service'; 

    $connect = mysqli_connect($dbhost, $dbuser, $dbpass) or die("Impossible de se connecter à '$dbhost'");
    mysqli_select_db($connect, $dbname) or die("Impossible d'ouvrir la base '$dbname'");

    $result = mysqli_query($connect, "SELECT id, product_name, product_price FROM products");
    ?>

    <table>
        <tr>
            <th>Numéro de produit</th>
            <th>Descriptif</th>
            <th>Prix</th>
        </tr>
        <?php while ($row = mysqli_fetch_array($result)) { ?>
            <tr>
                <td><?php echo $row['id']; ?></td>
                <td><?php echo $row['product_name']; ?></td>
                <td><?php echo $row['product_price']; ?> €</td>
            </tr>
        <?php } ?>
    </table>
</body>
</html>
