<?php
$host = 'mariadb_container_ip'; // Ou le nom du container si vous utilisez un network Docker
$user = 'root';
$pass = 'mypass';
$db   = 'woodytoys';

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("Échec de la connexion: " . $conn->connect_error);
}

echo "<h1>Catalogue WoodyToys - Groupe l1-10</h1>";
$sql = "SELECT id, product_name, product_price FROM products";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        echo "Produit: " . $row["product_name"]. " - Prix: " . $row["product_price"]. "€<br>";
    }
} else {
    echo "0 produits trouvés";
}
$conn->close();
?>
