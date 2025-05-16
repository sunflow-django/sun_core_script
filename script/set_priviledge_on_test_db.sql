CREATE DATABASE IF NOT EXISTS `operation`;
CREATE DATABASE IF NOT EXISTS `operation_test`;

GRANT ALL PRIVILEGES ON `operation`.* TO 'user'@'%';
GRANT ALL PRIVILEGES ON `operation_test`.* TO 'user'@'%';

FLUSH PRIVILEGES;
