const db_logic = require('./sqlite/db_logic');
// const get_matches = require('./get_matches');
const get_matches_rust = require('./get_matches_rust');

const parseABP = async () => {
  // start timer
  let start_time = Date.now();
  console.log('Starting rule parsing...');

  // Connect to database
  const { crawlDB, outputDB } = await db_logic.connectDatabases();

  // Get all the rows to insert into the output database
  let rowsToInsert = await get_matches_rust.getMatches(crawlDB);

  // Now that we have all the rows to insert, do it in a single transaction
  outputDB.serialize(() => {
    outputDB.run('BEGIN TRANSACTION');

    for (let row of rowsToInsert) {
      let insertQuery = `INSERT INTO ${row.type}_abp 
      (id, visit_id, site_url, ${
        row.type === 'http_requests' ? 'url' : 'script_url'
      }, top_level_url, easylist, easyprivacy, exceptionlist)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?);`;

      outputDB.run(insertQuery, row.data);
    }

    outputDB.run('COMMIT');
  });

  console.log('Total time: ' + (Date.now() - start_time));
};

parseABP();
