import zipfile

def create_table_postgresql():
    return """
CREATE TABLE contribuyentes
(
    ruc character varying(15) NOT NULL,
    razon_social character varying(300) NOT NULL,
    dv character varying(1) NOT NULL,
    ruc_str character varying(15) NOT NULL,
    CONSTRAINT pk_contribuyentes PRIMARY KEY (ruc )
);

CREATE INDEX ruc_index
ON contribuyentes
USING btree
(ruc COLLATE pg_catalog."default" );
    """


def insert_postgresql(ruc, razon_social, dv, ruc_str):
    razon_social = razon_social.replace("'", "''")
    ruc_str = ruc_str.replace("'", "''")
    return f"""INSERT INTO contribuyentes(ruc, razon_social, dv, ruc_str) VALUES ('{ruc}', '{razon_social}', '{dv}', '{ruc_str}');"""

def create_view_postgresql():
    return """
CREATE OR REPLACE VIEW ruc_contribuyentes AS 
SELECT pg_catalog.concat(contribuyentes.ruc, '-', contribuyentes.dv) AS ruc, 
        CASE
            WHEN substr(contribuyentes.ruc::text, 1, 1) <> '8'::text THEN substr(pg_catalog.concat(split_part(contribuyentes.razon_social::text, ','::text, 2), ' ', split_part(contribuyentes.razon_social::text, ','::text, 1)), 2, length(pg_catalog.concat(split_part(contribuyentes.razon_social::text, ','::text, 2), ' ', split_part(contribuyentes.razon_social::text, ','::text, 1))))::character varying
            ELSE contribuyentes.razon_social
        END AS razon_social
FROM contribuyentes;
    """



def file_compress(inp_file_names, out_zip_file):
    """
    function : file_compress
    args : inp_file_names : list of filenames to be zipped
    out_zip_file : output zip file
    return : none
    assumption : Input file paths and this code is in same directory.
    """
    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED
    print(f" *** Input File name passed for zipping - {inp_file_names}")

    # create the zip file first parameter path/name, second mode
    print(f' *** out_zip_file is - {out_zip_file}')
    zf = zipfile.ZipFile(out_zip_file, mode="w")

    try:
        for file_to_write in inp_file_names:
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            print(f' *** Processing file {file_to_write}')
            zf.write(file_to_write, file_to_write, compress_type=compression)
    except FileNotFoundError as e:
        print(f' *** Exception occurred during zip process - {e}')
    finally:
        # Don't forget to close the file!
        zf.close()