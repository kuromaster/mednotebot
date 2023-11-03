CREATE TABLE IF NOT EXISTS tb_customers (
    id               SERIAL PRIMARY KEY,
    tid              INTEGER UNIQUE NOT NULL,
    age              SMALLINT NULL,
    is_doctor        SMALLINT  DEFAULT 0,
    is_notify        SMALLINT  DEFAULT 1,
    is_administrator SMALLINT  DEFAULT 0,
    is_superuser     SMALLINT  DEFAULT 0,
    phonenumber      VARCHAR(20) NOT NULL,
    car_plate        VARCHAR(20) NULL,
    lastname         VARCHAR(50) NULL,
    name             VARCHAR(50) NULL,
    surname          VARCHAR(50) NULL,
    spreadsheet_id   VARCHAR(255) NULL,
    date_birth       TIMESTAMP NULL,
    date_reg         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tb_files (
    id          SERIAL PRIMARY KEY,
    tid         INTEGER     NOT NULL,
    filename    VARCHAR(30) NOT NULL,
    file_type   VARCHAR(15) NOT NULL,
    created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tb_appointments (
    id              SERIAL PRIMARY KEY,
    tid             INT NOT NULL,
    doctor_id       INT NOT NULL,
    appt_format     VARCHAR(15) NOT NULL, --   формат записи online, offline, closed
    description     VARCHAR(255) NULL,
    is_approved     SMALLINT DEFAULT 0, --     запись подтверждена
    is_notified     SMALLINT DEFAULT 0, --     клиенту послан запрос подтверждения
    is_closed       SMALLINT DEFAULT 0, --     день закрыт для записи
    appt_date       TIMESTAMP UNIQUE NOT NULL, --     дата записи
    approve_date    TIMESTAMP NULL, --     дата пациент подтвердил запись
    notify_date     TIMESTAMP NULL --     дата оповещения
);

CREATE TABLE IF NOT EXISTS tb_test (
    id              SERIAL PRIMARY KEY,
    appt_date       TIMESTAMP NOT NULL --     дата записи
);

ALTER TABLE tb_appointments ADD CONSTRAINT fk_tb_appointments_tid FOREIGN KEY (tid) REFERENCES tb_customers (tid) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE tb_files ADD CONSTRAINT fk_tb_files_tid FOREIGN KEY (tid) REFERENCES tb_customers (tid) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE tb_appointments OWNER TO dbuser;