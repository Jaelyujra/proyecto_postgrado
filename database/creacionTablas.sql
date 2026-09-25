BEGIN;
create table maestria(
	idMaestria serial primary key,	
	nomMaestria varchar(100) not null,
	siglaMaestria varchar(10) not null,
	versionMaestria varchar (10) not null,
	gestion smallint not null
);
create table estudiantePostgrado(
	idEstudiantePostgrado serial primary key,
	nombre varchar(20) not null,
	apellidoM varchar(20) not null,
	apellidoP varchar(20) not null,
	gradoAcademico varchar(5),
	idMaestria integer,
	constraint fkEstudiante_Maestria
		foreign key (idMaestria)
		references maestria(idMaestria)
);
create table docente(
	idDocente serial primary key,
	nombre varchar (20) not null,
	apellidoM varchar(20) not null,
	apellidoP varchar(20) not null
);
create table perfilTesis(
	idPerfil serial primary key,
	tituloPerfil varchar (100) not null,
	tituloProf varchar(20) not null,
	fecha date not null,
	idDocente integer,
	constraint fkPerfil_Docente
		foreign key (idDocente)
		references docente(idDocente),
	idEstudiantePostgrado integer,
	constraint fkEstudiantePostgrado_Perfil
		foreign key (idEstudiantePostgrado)
		references estudiantePostgrado(idEstudiantePostgrado)
);
create table resolucion(
	idResolucion serial primary key,
	enlace varchar(100),
	estado varchar(10),
	fechaRes date not null,
	observacion varchar(100),
	idPerfil integer,
	constraint fkResolucion_perfil
		foreign key (idPerfil)
		references perfilTesis(idPerfil)
);
create table tribunal(
	idTribunal serial primary key,
	idPerfil integer,
	constraint fkTribunal_perfil
		foreign key(idPerfil)
		references perfilTesis(idPerfil)
);
create table miembroTribunal(
	idMiembroTribunal serial primary key,
	rolDocente varchar(50),
	idDocente integer,
	constraint fkDocente_tribunal
		foreign key (idDocente)
		references docente(idDocente),
	idTribunal integer,
	constraint fkTribunal_trib
		foreign key (idTribunal)
		references tribunal(idTribunal)
);
COMMIT;
