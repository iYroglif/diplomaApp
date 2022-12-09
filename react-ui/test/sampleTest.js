module.exports = {
  "UI test": function (browser) {
    browser
      .url("http://localhost")
      .waitForElementVisible("body", 1000)
      .click("a[href='/about']")
      .waitForElementVisible(".about")
      .assert.containsText("h4", "Архитектура нейронной сети")
      .end();
  },
};
