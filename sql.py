DDL = """
  CREATE TABLE IF NOT EXISTS usuario (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NOME TEXT NOT NULL,
    SENHA TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS peso (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USUARIO_ID INTEGER NOT NULL,
    DATA_HORA DATETIME NOT NULL,
    NU_PESO_G TEXT NOT NULL,
    
    FOREIGN KEY(USUARIO_ID) REFERENCES usuario(ID)
  );
"""

DELETA_REGISTRO = """
  DELETE FROM peso WHERE DATE(DATA_HORA) = ?;
"""

INSERE_REGISTRO = """
  INSERT INTO peso (
    USUARIO_ID,
    DATA_HORA,
    NU_PESO_G
  ) VALUES (?, ?, ?);
"""

SELECIONA_REGISTRO_ID = """
  SELECT ID, USUARIO_ID, DATA_HORA, NU_PESO_G 
  FROM peso
  WHERE ID = ?;
"""

SELECIONA_REGISTRO_DATA_USUARIO_ID = """
  SELECT ID, USUARIO_ID, DATA_HORA, NU_PESO_G 
  FROM peso
  WHERE date(DATA_HORA) = ? AND USUARIO_ID = ?;
"""

ATUALIZA_REGISTRO_DATA_USUARIO_ID = """
  UPDATE peso SET
    DATA_HORA = ?,
    NU_PESO_G = ?
  WHERE date(DATA_HORA) = ? AND USUARIO_ID = ?;
"""

DDL_CALCULO = """
  CREATE TABLE peso (
    DATA_HORA DATETIME NOT NULL,
    NU_PESO_G INTEGER NOT NULL
  );
"""

CALCULO = """
  WITH CTE_WN AS (
    SELECT 
      DATA_HORA,
      NU_PESO_G,
      strftime('%W', datetime(DATA_HORA)) AS WN
    FROM peso
  ),
  CTE_MEDIA AS (
    SELECT 
      WN,
      AVG(NU_PESO_G) AS MEDIA
    FROM CTE_WN
    GROUP BY WN
  ),
  CTE_MAX_MIN AS (
      SELECT DISTINCT 
          WN,
          MIN(DATA_HORA) OVER (PARTITION BY WN) AS DE,
          MAX(DATA_HORA) OVER (PARTITION BY WN) AS ATÉ
      FROM CTE_WN
  )
  SELECT
      DATE(M.DE) AS DE,
      DATE(M.ATÉ) AS ATÉ,
      MEDIA.WN AS SEMANA,
      MEDIA.MEDIA AS [MÉDIA(gramas)],
      MEDIA.MEDIA/1000 AS [MÉDIA(Kg)]
  FROM CTE_MEDIA AS MEDIA
  LEFT JOIN CTE_MAX_MIN AS M ON M.WN = MEDIA.WN
  
"""