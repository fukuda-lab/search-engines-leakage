const fs = require('fs');
const adblockRust = require('adblock-rs');

const _getMatchesBlocksAndExceptions = (
  request,
  blocklistOnlyEngine,
  blocklistWithExceptionListEngine
) => {
  const url = request.url;
  const topLevelUrl = request.topLevelUrl;
  const resourceType = request.resourceType;

  let blocklist = 0;
  let exceptionList = 0;
  const blocklistResult = blocklistOnlyEngine.check(
    url,
    topLevelUrl,
    resourceType,
    true
  );
  if (blocklistResult.matched) {
    blocklist = 1;
    const exceptionListResult = blocklistWithExceptionListEngine.check(
      url,
      topLevelUrl,
      resourceType,
      true
    );
    if (exceptionListResult.exception) {
      exceptionList = 1;
    }
  }
  return { blocklist, exceptionList };
};

const getMatches = async (crawlDB) => {
  const easyListFilters = fs
    .readFileSync('./easylist.txt', { encoding: 'utf-8' })
    .split('\n');
  const easyPrivacyFilters = fs
    .readFileSync('./easyprivacy.txt', { encoding: 'utf-8' })
    .split('\n');
  const exceptionListFilters = fs
    .readFileSync('./exceptionrules.txt', { encoding: 'utf-8' })
    .split('\n');

  const debugInfo = true;

  const easyListOnlyFilterSet = new adblockRust.FilterSet(debugInfo);
  const easyListExceptionListFilterSet = new adblockRust.FilterSet(debugInfo);

  const easyPrivacyOnlyFilterSet = new adblockRust.FilterSet(debugInfo);
  const easyPrivacyExceptionListFilterSet = new adblockRust.FilterSet(
    debugInfo
  );

  easyListOnlyFilterSet.addFilters(easyListFilters);
  easyListExceptionListFilterSet.addFilters(easyListFilters);
  easyListExceptionListFilterSet.addFilters(exceptionListFilters);

  easyPrivacyOnlyFilterSet.addFilters(easyPrivacyFilters);
  easyPrivacyExceptionListFilterSet.addFilters(easyPrivacyFilters);
  easyPrivacyExceptionListFilterSet.addFilters(exceptionListFilters);

  const easyListOnlyEngine = new adblockRust.Engine(
    easyListOnlyFilterSet,
    true
  );
  const easyListExceptionListEngine = new adblockRust.Engine(
    easyListExceptionListFilterSet,
    true
  );

  const easyPrivacyOnlyEngine = new adblockRust.Engine(
    easyPrivacyOnlyFilterSet,
    true
  );
  const easyPrivacyExceptionListEngine = new adblockRust.Engine(
    easyPrivacyExceptionListFilterSet,
    true
  );

  let engines = [
    {
      name: 'easyList',
      blacklistOnlyEngine: easyListOnlyEngine,
      blacklistExceptionListEngine: easyListExceptionListEngine,
    },
    {
      name: 'easyPrivacy',
      blacklistOnlyEngine: easyPrivacyOnlyEngine,
      blacklistExceptionListEngine: easyPrivacyExceptionListEngine,
    },
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
              topLevelUrl: row.top_level_url,
              resourceType:
                type === 'http_requests' ? 'xmlhttprequest' : 'script',
            };

            let ruleResults = {
              easyList: 0,
              easyPrivacy: 0,
              exceptionList: 0,
            };

            // Check if the request matches the blocklist and exceptionList for each list (based on our new method)
            for (let engine of engines) {
              const { blocklist, exceptionList } =
                _getMatchesBlocksAndExceptions(
                  request,
                  engine.blacklistOnlyEngine,
                  engine.blacklistExceptionListEngine
                );

              // Assign the correct value to the ruleResults object
              ruleResults[engine.name] = blocklist;
              ruleResults['exceptionList'] += exceptionList;
            }
            if (ruleResults['exceptionList'] === 2) {
              ruleResults['exceptionList'] = 1;
              console.log('CASE FOUND');
            }

            // If any of the rules match, store the row data for later insertion
            if (
              ruleResults.easyList ||
              ruleResults.easyPrivacy ||
              ruleResults.exceptionList
            ) {
              rowsToInsert.push({
                type,
                data: [
                  row.id,
                  row.visit_id,
                  row.site_url,
                  type === 'http_requests' ? row.url : row.script_url,
                  row.top_level_url,
                  ruleResults.easyList,
                  ruleResults.easyPrivacy,
                  ruleResults.exceptionList,
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
