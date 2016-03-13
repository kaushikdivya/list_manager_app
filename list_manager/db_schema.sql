CREATE TABLE users(
    [id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name varchar(255) NOT NULL,
    email varchar(255) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    created_time DateTime default CURRENT_TIMESTAMP,
    modified_time DateTime on update CURRENT_TIMESTAMP,
    ]deleted_time DateTime default NULL
);

CREATE TABLE lists(
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id int,
    FOREIGN KEY (user_id) REFERENCES user(id),
    name varchar(255) NOT NULL,
    status varchar(255) NOT NULL,
    created_time DateTime default CURRENT_TIMESTAMP,
    modified_time DateTime on update CURRENT_TIMESTAMP,
    deleted_time DateTime default NULL
);

CREATE TABLE items(
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    list_id int,
    Foreign Key (list_id) References lists(id),
    name varchar(255) NOT NULL,
    quantity varchar(255),
    status varchar(255) NOT NULL,
    created_time DateTime default current_timestamp,
    modified_time DateTime on update CURRENT_TIMESTAMP,
    deleted_time DateTime default NULL
);

CREATE TABLE access_token(
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id int,
    Foreign Key (user_id) References users(id),
    access_token varchar(255) NOT NULL UNIQUE,
    created_time DateTime default current_timestamp,
    modified_time DateTime on update CURRENT_TIMESTAMP,
    deleted_time DateTime default null
);
