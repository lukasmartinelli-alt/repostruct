CREATE DATABASE repostruct;
CREATE SCHEMA import;
--Create import tables for copying data from CSV
CREATE TABLE import.javascript (
    CHAR(255) repo,
    CHAR(255) filename,
    INTEGER filesize,
);

CREATE TABLE import.java (
    CHAR(255) repo,
    CHAR(255) filename,
    INTEGER filesize,
);

CREATE TABLE import.go (
    CHAR(255) repo,
    CHAR(255) filename,
    INTEGER filesize,
);

--Create import tables for copying data from CSV
CREATE TABLE public.filenames {
    CHAR(255) repo,
    CHAR(10) repo_language,
    CHAR(255) filename,
    INTEGER filesize,
};
