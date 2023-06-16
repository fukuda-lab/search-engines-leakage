const adblockRust = require('adblock-rs');
const fs = require('fs');

const debugInfo = true;
const filterSet = new adblockRust.FilterSet(debugInfo);

const easylistFilters = fs
  .readFileSync('./easylist.txt', { encoding: 'utf-8' })
  .split('\n');
const exampleFilter = ['@@example.com^'];
filterSet.addFilters(easylistFilters);
filterSet.addFilters(exampleFilter);

const engine = new adblockRust.Engine(filterSet, true);

// Simple match
console.log(
  engine.check(
    'http://ads.example.com',
    'http://example.com/helloworld',
    'xmlhttprequest',
    true
  )
);
// Simple match
console.log(
  engine.check(
    'http://ads.example.com',
    'http://facebook.com',
    'xmlhttprequest',
    true
  )
);
// Match with full details
console.log(
  engine.check(
    'http://example.com/-advertisement-icon.',
    'http://example.com/helloworld',
    'image',
    true
  )
);
// No match, but still with full details
console.log(
  engine.check(
    'https://github.githubassets.com/assets/frameworks-64831a3d.js',
    'https://github.com/brave',
    'script',
    true
  )
);
// Example that includes a redirect resource
console.log(
  engine.check(
    'https://bbci.co.uk/test/analytics.js',
    'https://bbc.co.uk',
    'script',
    true
  )
);

// Serialize the engine to an ArrayBuffer
const serializedArrayBuffer = engine.serializeRaw();
console.log(
  `Engine size: ${(serializedArrayBuffer.byteLength / 1024 / 1024).toFixed(
    2
  )} MB`
);
