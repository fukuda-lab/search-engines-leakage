const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const connectDatabases = async () => {
  console.log('Starting Database Connection...');

  // Create Tables Queries
  const createHttpRequestsTable = `
    CREATE TABLE IF NOT EXISTS http_requests_abp ( 
        id INTEGER PRIMARY KEY, 
        visit_id INTEGER, 
        site_url TEXT, 
        url TEXT, 
        top_level_url TEXT, 
        easylist INTEGER, 
        easyprivacy INTEGER, 
        exceptionlist INTEGER 
    ); 
    `;

  const createJavascriptsTable = `
    CREATE TABLE IF NOT EXISTS javascripts_abp ( 
        id INTEGER PRIMARY KEY, 
        visit_id INTEGER, 
        site_url TEXT, 
        script_url TEXT, 
        document_url TEXT, 
        top_level_url TEXT, 
        easylist INTEGER, 
        easyprivacy INTEGER, 
        exceptionlist INTEGER 
    );
    `;

  // SQLite3 Databases paths
  const CRAWL_DATA_PATH = path.resolve(
    __dirname,
    '../../../sqlite/[vpn_czech]10_crawls_results.sqlite'
  );
  const OUTPUT_PATH = path.resolve(
    __dirname,
    './[vpn_czech]10_crawls_adblock.sqlite'
  );

  // Create Tables async function
  const createTables = async (dataBase) => {
    return new Promise((resolve, reject) => {
      dataBase.run(createHttpRequestsTable, (err) => {
        if (err) {
          console.error(err.message);
          reject(err);
        } else {
          console.log('HTTP Requests table created successfully.');
          dataBase.run(createJavascriptsTable, (err) => {
            if (err) {
              console.error(err.message);
              reject(err);
            } else {
              console.log('Javascripts table created successfully.');
              resolve();
            }
          });
        }
      });
    });
  };

  let crawlDB = new sqlite3.Database(
    CRAWL_DATA_PATH,
    sqlite3.OPEN_READONLY,
    (err) => {
      if (err) {
        console.error(err.message);
      }
      console.log('Connected to the crawl database.');
    }
  );

  let outputDB = new sqlite3.Database(OUTPUT_PATH, (err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Connected to the output database.');
  });

  await createTables(outputDB);
  console.log('Database Connection Successful.');
  return { crawlDB, outputDB };
};

module.exports = { connectDatabases };
