const fs = require('fs');
const ABPFilterParser = require('abp-filter-parser');
const tldextract = require('tld-extract');

const getMatches = async (crawlDB) => {
  // Read and parse rule files
  let easyListTxt = fs.readFileSync('easylist.txt', 'utf-8');
  let easyPrivacyTxt = fs.readFileSync('easyprivacy.txt', 'utf-8');
  let exceptionListTxt = fs.readFileSync('exceptionrules.txt', 'utf-8');

  let easyListData = {};
  let easyPrivacyData = {};
  let exceptionListData = {};

  ABPFilterParser.parse(easyListTxt, easyListData);
  ABPFilterParser.parse(easyPrivacyTxt, easyPrivacyData);
  ABPFilterParser.parse(exceptionListTxt, exceptionListData);

  let options = {
    script: true,
    image: false,
    stylesheet: false,
    object: false,
    xmlhttprequest: false,
    'object-subrequest': false,
    subdocument: false,
    document: false,
    elemhide: false,
    other: false,
    background: false,
    xbl: false,
    ping: false,
    dtd: false,
    media: false,
    'third-party': false,
    'match-case': false,
    collapse: false,
    donottrack: false,
    websocket: false,
  };

  let rulesets = [
    { name: 'easylist', data: easyListData },
    { name: 'easyprivacy', data: easyPrivacyData },
    { name: 'exceptionlist', data: exceptionListData },
  ];

  let queries = {
    http_requests: `SELECT hr.id, sv.visit_id, sv.site_url, hr.url, hr.top_level_url FROM site_visits sv INNER JOIN http_requests hr ON sv.visit_id = hr.visit_id;`,
    javascripts: `SELECT js.id, sv.visit_id, sv.site_url, js.script_url, js.document_url, js.top_level_url FROM site_visits sv INNER JOIN javascript js ON sv.visit_id = js.visit_id;`,
  };
  let i = 0;
  let rowsToInsert = [];
  let promises = [];

  for (let type in queries) {
    promises.push(
      new Promise((resolve, reject) => {
        crawlDB.each(
          queries[type],
          (err, row) => {
            if (err) {
              console.error(err.message);
              reject(err);
            }

            let request = {
              url: type === 'http_requests' ? row.url : row.script_url,
              topLevelUrl: tldextract(row.top_level_url).domain,
              options: options,
            };

            let ruleResults = {};

            for (let ruleset of rulesets) {
              if (
                ABPFilterParser.matches(ruleset.data, request.url, {
                  domain: request.topLevelUrl,
                  elementTypeMask: ABPFilterParser.elementTypes.all,
                })
              ) {
                ruleResults[ruleset.name] = 1;
              } else {
                ruleResults[ruleset.name] = 0;
              }
            }

            // If any of the rules match, store the row data for later insertion
            if (
              ruleResults.easylist ||
              ruleResults.easyprivacy ||
              ruleResults.exceptionlist
            ) {
              rowsToInsert.push({
                type,
                data: [
                  row.id,
                  row.visit_id,
                  row.site_url,
                  type === 'http_requests' ? row.url : row.script_url,
                  row.top_level_url,
                  ruleResults.easylist,
                  ruleResults.easyprivacy,
                  ruleResults.exceptionlist,
                ],
              });
            }

            if (i % 500 === 0 && i > 499) {
              console.log(`Progress: ${Math.round((i * 100) / 36080)}%`);
            }
            i += 1;
          },
          () => {
            resolve();
          }
        );
      })
    );
  }
  await Promise.all(promises);
  return rowsToInsert;
};

module.exports = { getMatches };
