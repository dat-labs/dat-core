CREATE DATABASE dat_backend;

INSERT INTO organizations (id,"name") VALUES
	 ('org-uuid','Org');

INSERT INTO workspaces (id,organization_id,"name") VALUES
	 ('wkspc-uuid','org-uuid','Default');

INSERT INTO actors (id,"name",icon,actor_type) VALUES
	 ('gdrive-uuid','google_drive',NULL,'source');

INSERT INTO users (id,email,created_at,updated_at,password_hash) VALUES
	 ('09922bd9-7872-4664-99d0-08eae42fb554','user@dat.com','2024-03-19 18:11:21.886584','2024-03-19 18:55:37.549741','$2b$12$cPKSF7MMlbnVJwocGH7YqecnwmllTHV8FMNcfrI.aBK/NNNSYwpyC');


INSERT INTO workspace_users (id,workspace_id,user_id,created_at,updated_at) VALUES
	 ('36b1c935-44da-4d33-b570-598bf6a4adf7','wkspc-uuid','09922bd9-7872-4664-99d0-08eae42fb554','2024-03-19 18:11:55.3905','2024-03-19 18:11:55.3905');

INSERT INTO actor_instances (id,workspace_id,actor_id,user_id,"name","configuration",actor_type,status,created_at,updated_at) VALUES
	 ('d6662db2-fd9e-47c3-95f6-1163aa56f321','wkspc-uuid','gdrive-uuid','09922bd9-7872-4664-99d0-08eae42fb554',NULL,NULL,NULL,'active','2024-03-22 17:54:08.101646','2024-03-22 17:54:08.101646');

INSERT INTO connections (id,"name",source_instance_id,generator_instance_id,destination_instance_id,"configuration","catalog",cron_string,status,created_at,updated_at) VALUES
	 ('b56f1b30-7eb9-4ecd-b05d-a6548ec68cbd',NULL,'d6662db2-fd9e-47c3-95f6-1163aa56f321','d6662db2-fd9e-47c3-95f6-1163aa56f321','d6662db2-fd9e-47c3-95f6-1163aa56f321',NULL,NULL,NULL,'active','2024-03-22 17:54:53.268063','2024-03-22 17:54:53.268063');

