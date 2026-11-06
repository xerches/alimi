import test from "node:test";
import assert from "node:assert/strict";
import { faqFrameworkIds, frameworkFaq, fill } from "../src/lib/faq.js";
import { choosableFrameworks, platform, quote } from "../src/lib/config.js";

test("every framework mapped today has five questions, and no other framework has any", () => {
  const mapped = choosableFrameworks().filter((f) => f.mapped).map((f) => f.id).sort();
  assert.deepEqual(faqFrameworkIds().sort(), mapped);
  for (const id of mapped) {
    const faq = frameworkFaq(id);
    assert.equal(faq.length, 5, `${id} has ${faq.length} questions`);
    for (const { q, a } of faq) {
      assert.ok(q.endsWith("?"), `${id}: question without a question mark: ${q}`);
      assert.ok(a.length > 80, `${id}: short answer to ${q}`);
      assert.ok(!/\{\{/.test(q + a), `${id}: unfilled token in ${q}`);
    }
  }
});

test("the cost question quotes the Silver price and says the audit fee is separate where there is one", () => {
  const silver = platform().tiers[0];
  for (const id of faqFrameworkIds()) {
    const cost = frameworkFaq(id).find((f) => /cost/i.test(f.q));
    assert.ok(cost, `${id} has no cost question`);
    assert.ok(cost.a.includes(silver.perUser), `${id}: the cost answer does not quote ${silver.perUser}`);
    assert.ok(/separate|no audit|no certification body/i.test(cost.a), `${id}: the cost answer does not separate the audit fee`);
  }
  assert.ok(frameworkFaq("insurer")[1].a.includes(quote({ tierId: "silver", users: 25 }).yearlyText));
});

test("an unknown token fails instead of printing braces", () => {
  assert.throws(() => fill("Costs {{nothing}}"), /unknown token/);
  assert.equal(fill("{{brand}} on {{silverName}}"), "Alimi on Silver");
});
