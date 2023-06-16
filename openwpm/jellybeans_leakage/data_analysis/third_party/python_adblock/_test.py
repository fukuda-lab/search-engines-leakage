from adblockparser import AdblockRules

with open("easylist.txt", "r") as f:
    # raw_rules = f.read().decode("utf8").splitlines()
    raw_rules = f.readlines()
rules = AdblockRules(raw_rules, {"third-party": True})
print(rules.should_block("http://ads.example.com"))
