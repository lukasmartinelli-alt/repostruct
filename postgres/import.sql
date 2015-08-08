COPY import.go FROM 'go.csv' WITH (
    FORMAT 'csv',
    DELIMITER ',',
    QUOTE '""'
)

INSERT INTO public.filenames
SELECT repo, 'go' as repo_language, filename, filesize
FROM import.javascript
