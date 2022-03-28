CREATE TABLE IF NOT EXISTS `Players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `home_world` varchar(30) NOT NULL,
  `discord_id` varchar(30) NULL,
  `first_seen` datetime NOT NULL DEFAULT current_timestamp(),
  `vip_tier` int(11) NOT NULL DEFAULT 0,
  `vip_expiration` datetime NULL,
  `vip_balance` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=148 DEFAULT CHARSET=utf8mb3;
