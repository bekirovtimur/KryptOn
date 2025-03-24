-- MySQL 10.13  Distrib 8.4.4, for Linux (x86_64)

DROP TABLE IF EXISTS `tariffs`;
CREATE TABLE `tariffs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `period` int NOT NULL,
  `region` varchar(255) NOT NULL,
  `cost` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `tariffs` WRITE;
INSERT INTO `tariffs` VALUES (1,'Russia (30 days)',2592000,'RU',0),(2,'Finland (30 days)',2592000,'FI',0),(3,'Turkey (30 days)',2592000,'TR',0),(4,'Germany (30 days)',2592000,'DE',0),(5,'Netherlands (30 days)',2592000,'NL',0),(6,'USA (30 days)',2592000,'US',0),(7,'Great Britain (30 days)',2592000,'GB',0);
UNLOCK TABLES;


DROP TABLE IF EXISTS `tokens`;
CREATE TABLE `tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `tariff_id` int NOT NULL,
  `token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `start_date` int NOT NULL,
  `end_date` int NOT NULL,
  `next_action` int NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`,`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chat_id` bigint NOT NULL,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `comment` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `tg_user_id` bigint DEFAULT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chat_id` (`chat_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

