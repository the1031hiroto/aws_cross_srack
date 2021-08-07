CREATE USER nativepassuser IDENTIFIED WITH mysql_native_password BY 'yyyyy';

CREATE TABLE IF not exists `crawl_histories` (
  `crawl_history_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'クロール履歴id',
  `crawl_url_id` int(10) unsigned NOT NULL COMMENT 'クロール対象ID',
  `is_changed` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '差分あり',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  `deleted` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '論理削除',
  `response_text` text,
  `diff` text,
  PRIMARY KEY (`crawl_history_id`),
  KEY `crawl_histories_IX1` (`crawl_url_id`)
) ENGINE=InnoDB AUTO_INCREMENT=180 DEFAULT CHARSET=utf8mb4 COMMENT='クロール履歴';
