let ABPFilterParser = require('abp-filter-parser');
var fs = require('fs');

let easyListTxt = fs.readFileSync('./easylist.txt', 'utf-8');
let parsedFilterData = {};
let urlToCheck = 'http://ads.example.com';

// This is the site who's URLs are being checked, not the domain of the URL being checked.
let currentPageDomain = 'slashdot.org';

ABPFilterParser.parse(easyListTxt, parsedFilterData);
// ABPFilterParser.parse(someOtherListOfFilters, parsedFilterData);

if (ABPFilterParser.matches(parsedFilterData, urlToCheck)) {
  console.log('You should block this URL!');
} else {
  console.log('You should NOT block this URL!');
}
