CREATE DATABASE IF NOT EXISTS MINERIADEDATOSPROYECTO;
USE MINERIADEDATOSPROYECTO;

CREATE TABLE IF NOT EXISTS cliente(
	cli_id INT NOT NULL AUTO_INCREMENT,
    cli_nombre VARCHAR(50) NOT NULL,
    cli_telefono VARCHAR(12) NOT NULL,
    PRIMARY KEY (cli_id),
    INDEX idx_cliente_nombre (cli_nombre),
    UNIQUE uni_telefono (cli_telefono)
);

CREATE TABLE IF NOT EXISTS empleado(
	emp_id INT NOT NULL AUTO_INCREMENT,
    emp_nombre VARCHAR(50) NOT NULL,
    emp_telefono VARCHAR(12) NOT NULL,
    PRIMARY KEY (emp_id),
    INDEX idx_empleado_nombre (emp_nombre),
    UNIQUE uni_telefono (emp_telefono)
);

CREATE TABLE IF NOT EXISTS evento(
	eve_id INT NOT NULL AUTO_INCREMENT,
    eve_fecha DATE NOT NULL,
    eve_numero_personas INT NOT NULL,
    eve_lugar VARCHAR(100) NOT NULL,  
	eve_preciototal DECIMAL(10,2) NOT NULL COMMENT 'Pesos MXN',
    eve_tipo SET('Basico', 'Personalizado') NOT NULL,
	eve_pago SET('No pagado', 'Pagado') NOT NULL,
	eve_tipodepago SET('Efectivo', 'Transferencia') NOT NULL,
    eve_cli_id INT NOT NULL,  
    PRIMARY KEY (eve_id, eve_cli_id),
    INDEX idx_evento_fecha (eve_fecha),
    UNIQUE uni_eve_fecha_cli(eve_fecha, eve_cli_id),
    CONSTRAINT fk_cli_eve
		FOREIGN KEY (eve_cli_id) 
		REFERENCES cliente(cli_id)
		ON DELETE RESTRICT
		ON UPDATE RESTRICT
);



