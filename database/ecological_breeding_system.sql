/*
 Navicat Premium Dump SQL

 Source Server         : localhost1
 Source Server Type    : MySQL
 Source Server Version : 80043 (8.0.43)
 Source Host           : localhost:3306
 Source Schema         : ecological_breeding_system

 Target Server Type    : MySQL
 Target Server Version : 80043 (8.0.43)
 File Encoding         : 65001

 Date: 10/05/2026 16:09:19
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_group
-- ----------------------------
INSERT INTO `auth_group` VALUES (1, 'vet');

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_group_permissions_group_id_permission_id_0cd325b0_uniq`(`group_id` ASC, `permission_id` ASC) USING BTREE,
  INDEX `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_permission_content_type_id_codename_01ab375a_uniq`(`content_type_id` ASC, `codename` ASC) USING BTREE,
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 69 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO `auth_permission` VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO `auth_permission` VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO `auth_permission` VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO `auth_permission` VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO `auth_permission` VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO `auth_permission` VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO `auth_permission` VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO `auth_permission` VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO `auth_permission` VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO `auth_permission` VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO `auth_permission` VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO `auth_permission` VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO `auth_permission` VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO `auth_permission` VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO `auth_permission` VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO `auth_permission` VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO `auth_permission` VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO `auth_permission` VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO `auth_permission` VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO `auth_permission` VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO `auth_permission` VALUES (21, 'Can add 用户基础信息', 6, 'add_user');
INSERT INTO `auth_permission` VALUES (22, 'Can change 用户基础信息', 6, 'change_user');
INSERT INTO `auth_permission` VALUES (23, 'Can delete 用户基础信息', 6, 'delete_user');
INSERT INTO `auth_permission` VALUES (24, 'Can view 用户基础信息', 6, 'view_user');
INSERT INTO `auth_permission` VALUES (25, 'Can add 养殖户信息', 7, 'add_farmerprofile');
INSERT INTO `auth_permission` VALUES (26, 'Can change 养殖户信息', 7, 'change_farmerprofile');
INSERT INTO `auth_permission` VALUES (27, 'Can delete 养殖户信息', 7, 'delete_farmerprofile');
INSERT INTO `auth_permission` VALUES (28, 'Can view 养殖户信息', 7, 'view_farmerprofile');
INSERT INTO `auth_permission` VALUES (29, 'Can add 资格认证', 8, 'add_certification');
INSERT INTO `auth_permission` VALUES (30, 'Can change 资格认证', 8, 'change_certification');
INSERT INTO `auth_permission` VALUES (31, 'Can delete 资格认证', 8, 'delete_certification');
INSERT INTO `auth_permission` VALUES (32, 'Can view 资格认证', 8, 'view_certification');
INSERT INTO `auth_permission` VALUES (33, 'Can add 管理员信息', 9, 'add_adminprofile');
INSERT INTO `auth_permission` VALUES (34, 'Can change 管理员信息', 9, 'change_adminprofile');
INSERT INTO `auth_permission` VALUES (35, 'Can delete 管理员信息', 9, 'delete_adminprofile');
INSERT INTO `auth_permission` VALUES (36, 'Can view 管理员信息', 9, 'view_adminprofile');
INSERT INTO `auth_permission` VALUES (37, 'Can add 牲畜大类', 10, 'add_livestockcategory');
INSERT INTO `auth_permission` VALUES (38, 'Can change 牲畜大类', 10, 'change_livestockcategory');
INSERT INTO `auth_permission` VALUES (39, 'Can delete 牲畜大类', 10, 'delete_livestockcategory');
INSERT INTO `auth_permission` VALUES (40, 'Can view 牲畜大类', 10, 'view_livestockcategory');
INSERT INTO `auth_permission` VALUES (41, 'Can add 牲畜批次', 11, 'add_livestockbatch');
INSERT INTO `auth_permission` VALUES (42, 'Can change 牲畜批次', 11, 'change_livestockbatch');
INSERT INTO `auth_permission` VALUES (43, 'Can delete 牲畜批次', 11, 'delete_livestockbatch');
INSERT INTO `auth_permission` VALUES (44, 'Can view 牲畜批次', 11, 'view_livestockbatch');
INSERT INTO `auth_permission` VALUES (45, 'Can add 养殖区域', 12, 'add_livestockarea');
INSERT INTO `auth_permission` VALUES (46, 'Can change 养殖区域', 12, 'change_livestockarea');
INSERT INTO `auth_permission` VALUES (47, 'Can delete 养殖区域', 12, 'delete_livestockarea');
INSERT INTO `auth_permission` VALUES (48, 'Can view 养殖区域', 12, 'view_livestockarea');
INSERT INTO `auth_permission` VALUES (49, 'Can add 疾病上报', 13, 'add_diseasereport');
INSERT INTO `auth_permission` VALUES (50, 'Can change 疾病上报', 13, 'change_diseasereport');
INSERT INTO `auth_permission` VALUES (51, 'Can delete 疾病上报', 13, 'delete_diseasereport');
INSERT INTO `auth_permission` VALUES (52, 'Can view 疾病上报', 13, 'view_diseasereport');
INSERT INTO `auth_permission` VALUES (53, 'Can add 饲料信息', 14, 'add_feedinfo');
INSERT INTO `auth_permission` VALUES (54, 'Can change 饲料信息', 14, 'change_feedinfo');
INSERT INTO `auth_permission` VALUES (55, 'Can delete 饲料信息', 14, 'delete_feedinfo');
INSERT INTO `auth_permission` VALUES (56, 'Can view 饲料信息', 14, 'view_feedinfo');
INSERT INTO `auth_permission` VALUES (57, 'Can add 疫苗接种', 15, 'add_vaccinationrecord');
INSERT INTO `auth_permission` VALUES (58, 'Can change 疫苗接种', 15, 'change_vaccinationrecord');
INSERT INTO `auth_permission` VALUES (59, 'Can delete 疫苗接种', 15, 'delete_vaccinationrecord');
INSERT INTO `auth_permission` VALUES (60, 'Can view 疫苗接种', 15, 'view_vaccinationrecord');
INSERT INTO `auth_permission` VALUES (61, 'Can add 喂养记录', 16, 'add_feedingrecord');
INSERT INTO `auth_permission` VALUES (62, 'Can change 喂养记录', 16, 'change_feedingrecord');
INSERT INTO `auth_permission` VALUES (63, 'Can delete 喂养记录', 16, 'delete_feedingrecord');
INSERT INTO `auth_permission` VALUES (64, 'Can view 喂养记录', 16, 'view_feedingrecord');
INSERT INTO `auth_permission` VALUES (65, 'Can add 质量溯源', 17, 'add_livestocktrace');
INSERT INTO `auth_permission` VALUES (66, 'Can change 质量溯源', 17, 'change_livestocktrace');
INSERT INTO `auth_permission` VALUES (67, 'Can delete 质量溯源', 17, 'delete_livestocktrace');
INSERT INTO `auth_permission` VALUES (68, 'Can view 质量溯源', 17, 'view_livestocktrace');

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `object_repr` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NULL DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `django_admin_log_content_type_id_c4bce8eb_fk_django_co`(`content_type_id` ASC) USING BTREE,
  INDEX `django_admin_log_user_id_c564eba6_fk_users_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `django_admin_log_chk_1` CHECK (`action_flag` >= 0)
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `django_content_type_app_label_model_76bd3d3b_uniq`(`app_label` ASC, `model` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO `django_content_type` VALUES (1, 'admin', 'logentry');
INSERT INTO `django_content_type` VALUES (3, 'auth', 'group');
INSERT INTO `django_content_type` VALUES (2, 'auth', 'permission');
INSERT INTO `django_content_type` VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES (12, 'livestock', 'livestockarea');
INSERT INTO `django_content_type` VALUES (11, 'livestock', 'livestockbatch');
INSERT INTO `django_content_type` VALUES (10, 'livestock', 'livestockcategory');
INSERT INTO `django_content_type` VALUES (13, 'production', 'diseasereport');
INSERT INTO `django_content_type` VALUES (14, 'production', 'feedinfo');
INSERT INTO `django_content_type` VALUES (16, 'production', 'feedingrecord');
INSERT INTO `django_content_type` VALUES (15, 'production', 'vaccinationrecord');
INSERT INTO `django_content_type` VALUES (5, 'sessions', 'session');
INSERT INTO `django_content_type` VALUES (17, 'traceability_app', 'livestocktrace');
INSERT INTO `django_content_type` VALUES (9, 'users', 'adminprofile');
INSERT INTO `django_content_type` VALUES (8, 'users', 'certification');
INSERT INTO `django_content_type` VALUES (7, 'users', 'farmerprofile');
INSERT INTO `django_content_type` VALUES (6, 'users', 'user');

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 78 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO `django_migrations` VALUES (1, 'contenttypes', '0001_initial', '2026-01-10 20:30:38.479016');
INSERT INTO `django_migrations` VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2026-01-10 20:30:38.544198');
INSERT INTO `django_migrations` VALUES (3, 'auth', '0001_initial', '2026-01-10 20:30:38.733320');
INSERT INTO `django_migrations` VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2026-01-10 20:30:38.780593');
INSERT INTO `django_migrations` VALUES (5, 'auth', '0003_alter_user_email_max_length', '2026-01-10 20:30:38.785209');
INSERT INTO `django_migrations` VALUES (6, 'auth', '0004_alter_user_username_opts', '2026-01-10 20:30:38.791519');
INSERT INTO `django_migrations` VALUES (7, 'auth', '0005_alter_user_last_login_null', '2026-01-10 20:30:38.797787');
INSERT INTO `django_migrations` VALUES (8, 'auth', '0006_require_contenttypes_0002', '2026-01-10 20:30:38.800902');
INSERT INTO `django_migrations` VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2026-01-10 20:30:38.807185');
INSERT INTO `django_migrations` VALUES (10, 'auth', '0008_alter_user_username_max_length', '2026-01-10 20:30:38.813869');
INSERT INTO `django_migrations` VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2026-01-10 20:30:38.819416');
INSERT INTO `django_migrations` VALUES (12, 'auth', '0010_alter_group_name_max_length', '2026-01-10 20:30:38.832457');
INSERT INTO `django_migrations` VALUES (13, 'auth', '0011_update_proxy_permissions', '2026-01-10 20:30:38.837090');
INSERT INTO `django_migrations` VALUES (14, 'auth', '0012_alter_user_first_name_max_length', '2026-01-10 20:30:38.844619');
INSERT INTO `django_migrations` VALUES (15, 'users', '0001_initial', '2026-01-10 20:30:39.165269');
INSERT INTO `django_migrations` VALUES (16, 'admin', '0001_initial', '2026-01-10 20:30:39.260369');
INSERT INTO `django_migrations` VALUES (17, 'admin', '0002_logentry_remove_auto_add', '2026-01-10 20:30:39.266512');
INSERT INTO `django_migrations` VALUES (18, 'admin', '0003_logentry_add_action_flag_choices', '2026-01-10 20:30:39.273137');
INSERT INTO `django_migrations` VALUES (19, 'users', '0002_operationlog', '2026-01-10 20:30:39.334536');
INSERT INTO `django_migrations` VALUES (20, 'users', '0003_remove_adminprofile_avatar_user_avatar', '2026-01-10 20:30:39.408790');
INSERT INTO `django_migrations` VALUES (21, 'users', '0004_delete_operationlog', '2026-01-10 20:30:39.421795');
INSERT INTO `django_migrations` VALUES (22, 'users', '0005_remove_certification_business_license_and_more', '2026-01-10 20:30:39.534289');
INSERT INTO `django_migrations` VALUES (23, 'users', '0006_remove_user_role', '2026-01-10 20:30:39.583495');
INSERT INTO `django_migrations` VALUES (24, 'livestock', '0001_initial', '2026-01-10 20:30:39.702927');
INSERT INTO `django_migrations` VALUES (25, 'livestock', '0002_initial', '2026-01-10 20:30:39.847096');
INSERT INTO `django_migrations` VALUES (26, 'livestock', '0003_alter_livestockbatch_status', '2026-01-10 20:30:39.867263');
INSERT INTO `django_migrations` VALUES (27, 'livestock', '0004_livestockarea_image', '2026-01-10 20:30:39.908600');
INSERT INTO `django_migrations` VALUES (28, 'livestock', '0005_remove_livestockcategory_icon_and_more', '2026-01-10 20:30:39.981635');
INSERT INTO `django_migrations` VALUES (29, 'livestock', '0006_livestockarea_area_size_livestockarea_breeding_type_and_more', '2026-01-10 20:30:40.094458');
INSERT INTO `django_migrations` VALUES (30, 'livestock', '0007_remove_livestockcategory_description', '2026-01-10 20:30:40.126391');
INSERT INTO `django_migrations` VALUES (31, 'livestock', '0008_remove_livestockbatch_area_delete_livestockarea', '2026-01-10 20:30:40.209251');
INSERT INTO `django_migrations` VALUES (32, 'livestock', '0009_livestockarea_livestockbatch_area', '2026-01-10 20:30:40.330912');
INSERT INTO `django_migrations` VALUES (33, 'livestock', '0010_livestockcategory_description', '2026-01-10 20:30:40.365548');
INSERT INTO `django_migrations` VALUES (34, 'livestock', '0011_livestockcategory_category_code', '2026-01-10 20:30:40.398645');
INSERT INTO `django_migrations` VALUES (35, 'livestock', '0012_alter_livestockarea_location_code', '2026-01-10 20:30:40.420669');
INSERT INTO `django_migrations` VALUES (36, 'livestock', '0013_remove_livestockarea_area_size_and_more', '2026-01-10 20:30:40.641892');
INSERT INTO `django_migrations` VALUES (37, 'livestock', '0014_alter_livestockbatch_status', '2026-01-10 20:30:40.647950');
INSERT INTO `django_migrations` VALUES (38, 'livestock', '0015_livestockbatch_image', '2026-01-10 20:30:40.686980');
INSERT INTO `django_migrations` VALUES (39, 'livestock', '0016_alter_livestockbatch_category', '2026-01-10 20:30:40.792307');
INSERT INTO `django_migrations` VALUES (40, 'livestock', '0017_livestockbatch_birth_date_livestockbatch_breed_and_more', '2026-01-10 20:30:41.101288');
INSERT INTO `django_migrations` VALUES (41, 'livestock', '0018_remove_livestockbatch_birth_date', '2026-01-10 20:30:41.142848');
INSERT INTO `django_migrations` VALUES (42, 'livestock', '0019_alter_livestockbatch_area', '2026-01-10 20:30:41.152032');
INSERT INTO `django_migrations` VALUES (43, 'livestock', '0020_alter_livestockcategory_options_and_more', '2026-01-10 20:30:41.263942');
INSERT INTO `django_migrations` VALUES (44, 'livestock', '0021_alter_livestockbatch_status', '2026-01-10 20:30:41.271706');
INSERT INTO `django_migrations` VALUES (45, 'livestock', '0022_livestockbatch_finish_date', '2026-01-10 20:30:41.321569');
INSERT INTO `django_migrations` VALUES (46, 'livestock', '0023_fix_livestockcategory_fixed_six', '2026-01-10 20:30:41.336606');
INSERT INTO `django_migrations` VALUES (47, 'livestock', '0024_rename_livestockbatch_entry_date_to_birth_date', '2026-01-10 20:30:41.364273');
INSERT INTO `django_migrations` VALUES (48, 'livestock', '0025_remove_livestockbatch_name', '2026-01-10 20:30:41.423208');
INSERT INTO `django_migrations` VALUES (49, 'production', '0001_initial', '2026-01-10 20:30:41.598548');
INSERT INTO `django_migrations` VALUES (50, 'production', '0002_initial', '2026-01-10 20:30:41.691529');
INSERT INTO `django_migrations` VALUES (51, 'production', '0003_alter_diseasereport_report_date', '2026-01-10 20:30:41.707354');
INSERT INTO `django_migrations` VALUES (52, 'production', '0004_feedinfo_created_at', '2026-01-10 20:30:41.756809');
INSERT INTO `django_migrations` VALUES (53, 'production', '0005_alter_feedinfo_created_at', '2026-01-10 20:30:41.765312');
INSERT INTO `django_migrations` VALUES (54, 'production', '0006_feedingrecord_remark_and_more', '2026-01-10 20:30:41.811553');
INSERT INTO `django_migrations` VALUES (55, 'production', '0007_vaccinationrecord_next_vaccination_date_and_more', '2026-01-10 20:30:41.851529');
INSERT INTO `django_migrations` VALUES (56, 'production', '0008_feedinfo_image_feedinfo_introduction', '2026-01-10 20:30:41.929111');
INSERT INTO `django_migrations` VALUES (57, 'production', '0009_remove_feedinfo_unit', '2026-01-10 20:30:41.967402');
INSERT INTO `django_migrations` VALUES (58, 'production', '0010_feedinfo_unit', '2026-01-10 20:30:42.017023');
INSERT INTO `django_migrations` VALUES (59, 'production', '0011_unitconfig_feedinfo_original_quantity_and_more', '2026-01-10 20:30:42.222103');
INSERT INTO `django_migrations` VALUES (60, 'production', '0012_delete_unitconfig_remove_feedinfo_original_quantity_and_more', '2026-01-10 20:30:42.381915');
INSERT INTO `django_migrations` VALUES (61, 'production', '0013_remove_feedinfo_brand', '2026-01-10 20:30:42.418507');
INSERT INTO `django_migrations` VALUES (62, 'production', '0014_diseasereport_treatment_plan_and_handler', '2026-01-10 20:30:42.539055');
INSERT INTO `django_migrations` VALUES (63, 'production', '0015_diseasereport_assigned_vet', '2026-01-10 20:30:42.597504');
INSERT INTO `django_migrations` VALUES (64, 'production', '0016_remove_diseasereport_assigned_vet', '2026-01-10 20:30:42.669339');
INSERT INTO `django_migrations` VALUES (65, 'production', '0017_alter_feedinfo_unit', '2026-01-10 20:30:42.678558');
INSERT INTO `django_migrations` VALUES (66, 'sessions', '0001_initial', '2026-01-10 20:30:42.708813');
INSERT INTO `django_migrations` VALUES (67, 'traceability_app', '0001_initial', '2026-01-10 20:30:42.793529');
INSERT INTO `django_migrations` VALUES (68, 'traceability_app', '0002_remove_livestocktrace_query_count', '2026-01-10 20:30:42.833869');
INSERT INTO `django_migrations` VALUES (69, 'traceability_app', '0003_livestocktrace_qr_code_image', '2026-01-10 20:30:42.875691');
INSERT INTO `django_migrations` VALUES (70, 'users', '0007_alter_certification_id_card_and_more', '2026-01-10 20:30:42.974836');
INSERT INTO `django_migrations` VALUES (71, 'users', '0008_alter_farmerprofile_address_and_more', '2026-01-10 20:30:43.067765');
INSERT INTO `django_migrations` VALUES (72, 'users', '0009_vetprofile', '2026-01-10 20:30:43.130351');
INSERT INTO `django_migrations` VALUES (73, 'users', '0010_delete_vetprofile', '2026-01-10 20:30:43.142051');
INSERT INTO `django_migrations` VALUES (74, 'users', '0011_create_default_vet_user', '2026-01-10 20:30:43.437534');
INSERT INTO `django_migrations` VALUES (75, 'livestock', '0026_remove_simmental_category', '2026-01-17 15:31:34.426247');
INSERT INTO `django_migrations` VALUES (76, 'livestock', '0027_set_default_standard_cycle_for_six_categories', '2026-01-17 20:50:37.690919');
INSERT INTO `django_migrations` VALUES (77, 'livestock', '0028_rename_livestockbatch_birth_date_to_entry_date', '2026-01-18 11:27:28.077781');

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session`  (
  `session_key` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`) USING BTREE,
  INDEX `django_session_expire_date_a5c62663`(`expire_date` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_session
-- ----------------------------
INSERT INTO `django_session` VALUES ('9lltwjcizjl0v4d8rgqtbj86s2x75f3c', '.eJxVjMEOwiAQBf-FsyFAoYBH7_0GAruLVA0kpT0Z_9026UGvM_Pem4W4rSVsnZYwI7syyS6_LEV4Uj0EPmK9Nw6trsuc-JHw03Y-NaTX7Wz_DkrsZV9DtqPzPksbszGoBCnjQCaD2Tht5QCSnPIiEQihPUatR73DhAMpZyT7fAHczzd2:1vhq56:CG02yoEC348BtW7xjyi2NA3z5saV76dTFPjPAY2x-BY', '2026-02-02 22:18:12.850200');
INSERT INTO `django_session` VALUES ('ngtufpohkj8dqv3xfbp7suilrfvswb84', '.eJxVjMEOwiAQBf-FsyFAoYBH7_0GAruLVA0kpT0Z_9026UGvM_Pem4W4rSVsnZYwI7syyS6_LEV4Uj0EPmK9Nw6trsuc-JHw03Y-NaTX7Wz_DkrsZV9DtqPzPksbszGoBCnjQCaD2Tht5QCSnPIiEQihPUatR73DhAMpZyT7fAHczzd2:1vhqS1:gEnWQt4ZCJHnnMJSclta829J5GXsDGqrIvaSOkOKxfM', '2026-02-02 22:41:53.035551');

-- ----------------------------
-- Table structure for livestock_area
-- ----------------------------
DROP TABLE IF EXISTS `livestock_area`;
CREATE TABLE `livestock_area`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `area_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `farmer_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `livestock_area_farmer_id_08e08395_fk_users_farmer_profile_id`(`farmer_id` ASC) USING BTREE,
  CONSTRAINT `livestock_area_farmer_id_08e08395_fk_users_farmer_profile_id` FOREIGN KEY (`farmer_id`) REFERENCES `users_farmer_profile` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 29 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of livestock_area
-- ----------------------------
INSERT INTO `livestock_area` VALUES (16, '1号牛舍', 'areas/2.jpg', '1号牛舍1号牛舍1号牛舍', 14);
INSERT INTO `livestock_area` VALUES (17, '2号牛舍', 'areas/Snipaste_2026-05-08_14-56-20.png', '1号牛舍1号牛舍1号牛舍', 14);
INSERT INTO `livestock_area` VALUES (18, '1号鸡舍', 'areas/VCG211300558407.jpg', '', 14);
INSERT INTO `livestock_area` VALUES (19, '1号鸭舍', 'areas/v2-671bf96059d422ba0d86b2b26296e17e_r.jpg', '', 14);
INSERT INTO `livestock_area` VALUES (20, '1号鹅舍', 'areas/OIP-C_yxKhVGC.jpg', '', 14);
INSERT INTO `livestock_area` VALUES (21, '1号羊舍', 'areas/Snipaste_2026-05-08_12-30-24.png', '', 14);
INSERT INTO `livestock_area` VALUES (22, '1号猪舍', 'areas/2089.jpg_wh860.jpg', '大白猪', 14);
INSERT INTO `livestock_area` VALUES (25, '9号牛舍', 'areas/image_2_OzC1jiJ.jpg', '', 15);

-- ----------------------------
-- Table structure for livestock_batch
-- ----------------------------
DROP TABLE IF EXISTS `livestock_batch`;
CREATE TABLE `livestock_batch`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `batch_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int NOT NULL,
  `entry_date` date NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` bigint NULL DEFAULT NULL,
  `farmer_id` bigint NOT NULL,
  `area_id` bigint NULL DEFAULT NULL,
  `image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `breed` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `introduction` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `livestock_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `finish_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `batch_code`(`batch_code` ASC) USING BTREE,
  INDEX `livestock_batch_farmer_id_1e14054e_fk_users_farmer_profile_id`(`farmer_id` ASC) USING BTREE,
  INDEX `livestock_batch_status_1e19383d`(`status` ASC) USING BTREE,
  INDEX `livestock_batch_area_id_360ea309_fk_livestock_area_id`(`area_id` ASC) USING BTREE,
  INDEX `livestock_batch_category_id_9f0c9bb1_fk_livestock_category_id`(`category_id` ASC) USING BTREE,
  CONSTRAINT `livestock_batch_area_id_360ea309_fk_livestock_area_id` FOREIGN KEY (`area_id`) REFERENCES `livestock_area` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `livestock_batch_category_id_9f0c9bb1_fk_livestock_category_id` FOREIGN KEY (`category_id`) REFERENCES `livestock_category` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `livestock_batch_farmer_id_1e14054e_fk_users_farmer_profile_id` FOREIGN KEY (`farmer_id`) REFERENCES `users_farmer_profile` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 25 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of livestock_batch
-- ----------------------------
INSERT INTO `livestock_batch` VALUES (12, 'A20260117F0014001', 50, '2026-01-17', 'finished', 8, 14, 18, 'batches/image_1_sWKPmrG.jpg', '三黄鸡', '公', '生长环境非常好', '鸡', '2026-03-11');
INSERT INTO `livestock_batch` VALUES (13, 'B20260117F0014001', 25, '2026-01-17', 'finished', 9, 14, 19, 'batches/Snipaste_2026-05-08_12-49-03.png', '', '混养', '', '鸭', '2026-01-24');
INSERT INTO `livestock_batch` VALUES (14, 'C20260117F0014001', 100, '2026-01-17', 'finished', 10, 14, 20, 'batches/Snipaste_2026-05-08_12-49-24.png', '大白鹅', '混养', '', '鹅', '2026-05-08');
INSERT INTO `livestock_batch` VALUES (15, 'D20260118F0014001', 10, '2026-01-14', 'active', 11, 14, 17, 'batches/Snipaste_2026-05-08_12-49-53.png', '大黄牛', '母', '', '牛', NULL);
INSERT INTO `livestock_batch` VALUES (19, 'A20260311F0014001', 20, '2026-03-11', 'finished', 8, 14, 18, 'batches/Snipaste_2026-05-08_12-48-37.png', '', '公', '1234', '鸡', '2026-05-08');
INSERT INTO `livestock_batch` VALUES (20, 'F20260508F0014001', 20, '2025-12-01', 'active', 13, 14, 22, 'batches/Snipaste_2026-05-08_12-50-39.png', '', '混养', '', '猪', NULL);

-- ----------------------------
-- Table structure for livestock_category
-- ----------------------------
DROP TABLE IF EXISTS `livestock_category`;
CREATE TABLE `livestock_category`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `category_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `icon` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `standard_cycle` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `category_code`(`category_code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of livestock_category
-- ----------------------------
INSERT INTO `livestock_category` VALUES (8, '鸡', NULL, 'A', '', 45);
INSERT INTO `livestock_category` VALUES (9, '鸭', NULL, 'B', '', 50);
INSERT INTO `livestock_category` VALUES (10, '鹅', NULL, 'C', '', 80);
INSERT INTO `livestock_category` VALUES (11, '牛', NULL, 'D', '', 540);
INSERT INTO `livestock_category` VALUES (12, '羊', NULL, 'E', '', 180);
INSERT INTO `livestock_category` VALUES (13, '猪', NULL, 'F', '', 180);

-- ----------------------------
-- Table structure for production_disease
-- ----------------------------
DROP TABLE IF EXISTS `production_disease`;
CREATE TABLE `production_disease`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `disease_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `symptoms` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `affected_count` int NOT NULL,
  `report_date` date NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch_id` bigint NOT NULL,
  `treatment_plan` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `handled_at` datetime(6) NULL DEFAULT NULL,
  `handled_by_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `production_disease_batch_id_95a8a799_fk_livestock_batch_id`(`batch_id` ASC) USING BTREE,
  INDEX `production_disease_report_date_1d00da25`(`report_date` ASC) USING BTREE,
  INDEX `production_disease_handled_by_id_d6bbd58e_fk_users_user_id`(`handled_by_id` ASC) USING BTREE,
  CONSTRAINT `production_disease_batch_id_95a8a799_fk_livestock_batch_id` FOREIGN KEY (`batch_id`) REFERENCES `livestock_batch` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `production_disease_handled_by_id_d6bbd58e_fk_users_user_id` FOREIGN KEY (`handled_by_id`) REFERENCES `users_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of production_disease
-- ----------------------------
INSERT INTO `production_disease` VALUES (2, '鹅瘟', '鹅瘟鹅瘟鹅瘟', 2, '2026-01-17', 'pending', 14, NULL, NULL, NULL);
INSERT INTO `production_disease` VALUES (3, '鸭感冒', '鸭感冒鸭感冒', 4, '2026-01-17', 'pending', 13, NULL, NULL, 2);
INSERT INTO `production_disease` VALUES (4, '鸡瘟', '鸡瘟', 3, '2026-05-08', 'recovered', 19, '', '2026-05-08 16:00:16.570753', 2);

-- ----------------------------
-- Table structure for production_feed
-- ----------------------------
DROP TABLE IF EXISTS `production_feed`;
CREATE TABLE `production_feed`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `feed_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `stock_quantity` decimal(10, 2) NOT NULL,
  `farmer_id` bigint NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `introduction` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `unit` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `production_feed_farmer_id_33c66afa_fk_users_farmer_profile_id`(`farmer_id` ASC) USING BTREE,
  CONSTRAINT `production_feed_farmer_id_33c66afa_fk_users_farmer_profile_id` FOREIGN KEY (`farmer_id`) REFERENCES `users_farmer_profile` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of production_feed
-- ----------------------------
INSERT INTO `production_feed` VALUES (10, '鸡饲料1号', 43.00, 14, '2026-01-17 19:26:08.563436', 'feeds/Snipaste_2026-05-08_12-54-36.png', '鸡饲料1号鸡饲料1号鸡饲料1号', 'kg');
INSERT INTO `production_feed` VALUES (11, '鸭饲料1号', 37.00, 14, '2026-01-17 19:26:49.664352', 'feeds/Snipaste_2026-05-08_12-53-34.png', '鸭饲料1号鸭饲料1号', 'kg');
INSERT INTO `production_feed` VALUES (12, '鹅饲料1号', 100.00, 14, '2026-01-17 19:56:07.891021', 'feeds/Snipaste_2026-05-08_12-52-50.png', '1111', 'kg');
INSERT INTO `production_feed` VALUES (13, '鸡饲料2号', 97.00, 14, '2026-01-17 20:05:46.553293', 'feeds/Snipaste_2026-05-08_12-52-23.png', '鸡饲料2号鸡饲料2号', 'kg');
INSERT INTO `production_feed` VALUES (14, '鸭饲料5号', 100.00, 15, '2026-03-22 20:07:53.733699', 'feeds/image_3.jpg', '123', 'kg');

-- ----------------------------
-- Table structure for production_feeding
-- ----------------------------
DROP TABLE IF EXISTS `production_feeding`;
CREATE TABLE `production_feeding`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `feed_weight` decimal(10, 2) NOT NULL,
  `feeding_time` datetime(6) NOT NULL,
  `batch_id` bigint NOT NULL,
  `feed_id` bigint NOT NULL,
  `remark` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `production_feeding_batch_id_1bf6a006_fk_livestock_batch_id`(`batch_id` ASC) USING BTREE,
  INDEX `production_feeding_feed_id_ecd82d41_fk_production_feed_id`(`feed_id` ASC) USING BTREE,
  CONSTRAINT `production_feeding_batch_id_1bf6a006_fk_livestock_batch_id` FOREIGN KEY (`batch_id`) REFERENCES `livestock_batch` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `production_feeding_feed_id_ecd82d41_fk_production_feed_id` FOREIGN KEY (`feed_id`) REFERENCES `production_feed` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of production_feeding
-- ----------------------------
INSERT INTO `production_feeding` VALUES (2, 3.00, '2026-01-17 19:36:28.745161', 12, 10, '111');
INSERT INTO `production_feeding` VALUES (3, 3.00, '2026-01-17 19:45:41.421482', 13, 11, '');
INSERT INTO `production_feeding` VALUES (5, 3.00, '2026-05-08 15:55:10.297499', 19, 13, '');
INSERT INTO `production_feeding` VALUES (6, 4.00, '2026-05-08 15:55:25.516108', 19, 10, '');

-- ----------------------------
-- Table structure for production_vaccine
-- ----------------------------
DROP TABLE IF EXISTS `production_vaccine`;
CREATE TABLE `production_vaccine`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `vaccine_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `vaccination_date` date NOT NULL,
  `remark` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `batch_id` bigint NOT NULL,
  `next_vaccination_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `production_vaccine_batch_id_77601de8_fk_livestock_batch_id`(`batch_id` ASC) USING BTREE,
  CONSTRAINT `production_vaccine_batch_id_77601de8_fk_livestock_batch_id` FOREIGN KEY (`batch_id`) REFERENCES `livestock_batch` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of production_vaccine
-- ----------------------------
INSERT INTO `production_vaccine` VALUES (2, '疫苗1号', '2026-01-17', '1234', 12, NULL);
INSERT INTO `production_vaccine` VALUES (3, '疫苗2号', '2026-01-17', '', 13, '2026-01-19');
INSERT INTO `production_vaccine` VALUES (4, '123', '2026-05-04', '', 14, '2026-05-12');
INSERT INTO `production_vaccine` VALUES (5, '感冒疫苗', '2026-04-08', '', 19, NULL);
INSERT INTO `production_vaccine` VALUES (6, '鸡瘟疫苗', '2026-04-21', '', 19, '2026-05-01');

-- ----------------------------
-- Table structure for traceability_app_livestocktrace
-- ----------------------------
DROP TABLE IF EXISTS `traceability_app_livestocktrace`;
CREATE TABLE `traceability_app_livestocktrace`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `trace_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `batch_id` bigint NOT NULL,
  `qr_code_image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `trace_code`(`trace_code` ASC) USING BTREE,
  UNIQUE INDEX `batch_id`(`batch_id` ASC) USING BTREE,
  CONSTRAINT `traceability_app_liv_batch_id_0b180e88_fk_livestock` FOREIGN KEY (`batch_id`) REFERENCES `livestock_batch` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of traceability_app_livestocktrace
-- ----------------------------
INSERT INTO `traceability_app_livestocktrace` VALUES (3, 'ECO17692331350A7DB6', 1, '2026-01-24 13:38:55.218523', 13, 'trace_qr_codes/trace_ECO17692331350A7DB6.png');
INSERT INTO `traceability_app_livestocktrace` VALUES (4, 'ECO17732300966E22BB', 1, '2026-03-11 19:54:56.443826', 12, 'trace_qr_codes/trace_ECO17732300966E22BB.png');
INSERT INTO `traceability_app_livestocktrace` VALUES (5, 'ECO1778221807C8CB6F', 1, '2026-05-08 14:30:07.671353', 14, 'trace_qr_codes/trace_ECO1778221807C8CB6F.png');
INSERT INTO `traceability_app_livestocktrace` VALUES (6, 'ECO1778227276C6A4B1', 1, '2026-05-08 16:01:16.232804', 19, 'trace_qr_codes/trace_ECO1778227276C6A4B1.png');

-- ----------------------------
-- Table structure for users_admin_profile
-- ----------------------------
DROP TABLE IF EXISTS `users_admin_profile`;
CREATE TABLE `users_admin_profile`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `users_admin_profile_user_id_8ccfe889_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users_admin_profile
-- ----------------------------
INSERT INTO `users_admin_profile` VALUES (1, '管理员', '系统管理', 1);

-- ----------------------------
-- Table structure for users_certification
-- ----------------------------
DROP TABLE IF EXISTS `users_certification`;
CREATE TABLE `users_certification`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `id_card_front` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` int NOT NULL,
  `audit_remark` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `audit_time` datetime(6) NULL DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `farmer_id` bigint NOT NULL,
  `breeding_license` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `id_card` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `id_card_back` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `users_certification_farmer_id_e51333ed_fk_users_far`(`farmer_id` ASC) USING BTREE,
  CONSTRAINT `users_certification_farmer_id_e51333ed_fk_users_far` FOREIGN KEY (`farmer_id`) REFERENCES `users_farmer_profile` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 22 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users_certification
-- ----------------------------
INSERT INTO `users_certification` VALUES (17, 'certs/id_cards/image_1_sQb5RWH.jpg', 1, '', '2026-01-17 19:17:54.354939', '2026-01-17 19:14:55.198308', 14, 'certs/licenses/image_3_1sqjnzQ.jpg', 'ENC_MTExMTExMTExMTExMTExMTEx', 'certs/id_cards/image_2_0G23Yoi.jpg');
INSERT INTO `users_certification` VALUES (18, 'certs/id_cards/image_2_d1AU6vr.jpg', 1, '', '2026-03-22 20:06:52.656187', '2026-01-17 19:16:13.532051', 15, 'certs/licenses/image_6.jpg', 'ENC_MjIyMjIyMjIyMjIyMjIyMjIy', 'certs/id_cards/image_5.jpg');
INSERT INTO `users_certification` VALUES (19, 'certs/id_cards/image_1_29Azz6x.jpg', 0, NULL, NULL, '2026-01-17 19:17:19.841874', 16, 'certs/licenses/image_2.jpg', 'ENC_MzMzMzMzMzMzMzMzMzMzMzMz', 'certs/id_cards/image_6.jpg');
INSERT INTO `users_certification` VALUES (20, 'certs/id_cards/image_5_sKJ4ubW.jpg', 0, NULL, NULL, '2026-03-22 20:06:09.645403', 11, 'certs/licenses/image_17.jpg', 'ENC_MTIzNDU2NzU3MzczNzM3Njc3', 'certs/id_cards/image_4.jpg');
INSERT INTO `users_certification` VALUES (21, 'certs/id_cards/Snipaste_2026-05-08_12-22-33.png', 0, NULL, NULL, '2026-05-08 12:57:51.952718', 17, 'certs/licenses/s_bed10bfbcb0c457095f3ad6fad61eff9.png', 'ENC_MTIzNDU2Nzg0MzI1MzI1MjM1', 'certs/id_cards/Snipaste_2026-05-08_12-22-56.png');

-- ----------------------------
-- Table structure for users_farmer_profile
-- ----------------------------
DROP TABLE IF EXISTS `users_farmer_profile`;
CREATE TABLE `users_farmer_profile`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `farmer_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_card` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `users_farmer_profile_user_id_6b9d3ffe_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users_farmer_profile
-- ----------------------------
INSERT INTO `users_farmer_profile` VALUES (11, 'farmer', NULL, NULL, 0, 13);
INSERT INTO `users_farmer_profile` VALUES (14, 'farmer1', 'ENC_MTExMTExMTExMTExMTExMTEx', NULL, 1, 16);
INSERT INTO `users_farmer_profile` VALUES (15, 'farmer2', 'ENC_MjIyMjIyMjIyMjIyMjIyMjIy', NULL, 1, 17);
INSERT INTO `users_farmer_profile` VALUES (16, 'farmer3', NULL, NULL, 0, 18);
INSERT INTO `users_farmer_profile` VALUES (17, 'farmer4', NULL, NULL, 0, 22);

-- ----------------------------
-- Table structure for users_user
-- ----------------------------
DROP TABLE IF EXISTS `users_user`;
CREATE TABLE `users_user`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) NULL DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `phone` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `phone`(`phone` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 23 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users_user
-- ----------------------------
INSERT INTO `users_user` VALUES (1, 'pbkdf2_sha256$600000$tCZmAXsO1N66vxG2oQxnIi$USqGuBozypxkZ1cqeNHkHjI5ZucPznGkd5K4neCfj0U=', '2026-01-19 22:41:53.032000', 1, 'admin', '', '', 'admin@example.com', 1, 1, '2026-01-17 12:37:10.095150', NULL, 'avatars/2026/01/admin_avatar.jpg');
INSERT INTO `users_user` VALUES (2, 'pbkdf2_sha256$600000$YeOxoGEQPZwkrn3Df85GHE$i3qIJn6GeCskJN4mrXrB/OS6ZHmksIWfxgsNeHy3WWg=', NULL, 0, 'vet', '', '', 'vet@example.com', 0, 1, '2026-01-17 12:40:38.882683', NULL, 'avatars/2026/01/vet_avatar.jpg');
INSERT INTO `users_user` VALUES (13, 'pbkdf2_sha256$600000$VFcZJ1AHu6XXR0xZ3BWh7W$aPjaCVQNvX+CdAKgYeWQFbgpS/7uiUHJG3A97jzTuPI=', NULL, 0, 'farmer', '', '', '', 0, 1, '2026-01-17 14:06:02.587867', NULL, 'avatars/2026/01/farmer_avatar.jpg');
INSERT INTO `users_user` VALUES (16, 'pbkdf2_sha256$600000$0lmBmRliQVA0mts6yWfp5Q$luKDKyn/6Jzqs0oO3A4QA49ztzW0e6kbbLPi6lE6OE4=', NULL, 0, 'farmer1', '', '', '', 0, 1, '2026-01-17 19:14:10.335708', NULL, 'avatars/2026/01/farmer1_avatar_vxgxleZ.jpg');
INSERT INTO `users_user` VALUES (17, 'pbkdf2_sha256$600000$43SGxGsNXRMViMR4Syjcli$De7OHxAVGeQhEYo5hpDMxyXsdYsyffGne8laorWAw6g=', NULL, 0, 'farmer2', '', '', '', 0, 1, '2026-01-17 19:15:31.267429', NULL, 'avatars/2026/03/farmer2_avatar.jpg');
INSERT INTO `users_user` VALUES (18, 'pbkdf2_sha256$600000$df0HvolyY8kCY1kycLkum4$HElTVLoU8P+I4xy1rSU7we1OM+8ftW6e0K2aywkHA1s=', NULL, 0, 'farmer3', '', '', '', 0, 1, '2026-01-17 19:16:40.805835', NULL, '');
INSERT INTO `users_user` VALUES (22, 'pbkdf2_sha256$600000$w7XqxNoEKKv9U0P1ShTRUk$D3J0TDXKbrgRVNIOl8C50eWy3u+ZQ+znqikDIDE/zk0=', NULL, 0, 'farmer4', '', '', '', 0, 1, '2026-05-08 12:56:47.881367', NULL, 'avatars/2026/05/farmer4_avatar.jpg');

-- ----------------------------
-- Table structure for users_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `users_user_groups`;
CREATE TABLE `users_user_groups`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `users_user_groups_user_id_group_id_b88eab82_uniq`(`user_id` ASC, `group_id` ASC) USING BTREE,
  INDEX `users_user_groups_group_id_9afc8d0e_fk_auth_group_id`(`group_id` ASC) USING BTREE,
  CONSTRAINT `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `users_user_groups_user_id_5f6f5a90_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users_user_groups
-- ----------------------------
INSERT INTO `users_user_groups` VALUES (1, 2, 1);

-- ----------------------------
-- Table structure for users_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS `users_user_user_permissions`;
CREATE TABLE `users_user_user_permissions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `users_user_user_permissions_user_id_permission_id_43338c45_uniq`(`user_id` ASC, `permission_id` ASC) USING BTREE,
  INDEX `users_user_user_perm_permission_id_0b93982e_fk_auth_perm`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `users_user_user_permissions_user_id_20aca447_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users_user_user_permissions
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
