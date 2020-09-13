const github = require("@actions/github");
const core = require("@actions/core");

const labelsToAdd = core.getInput("label");

async function label() {
  const myToken = core.getInput("repo-token");
  const octokit = new github.GitHub(myToken);
  const context = github.context;


  let timeline = await octokit.issues.listEventsForTimeline({
    owner: context.payload.repository.owner.login,
    repo: context.payload.repository.name,
    issue_number: context.payload.issue.number,
  });
  context.log(timeline);
}

comment()
  .then(
    result => {
      // eslint-disable-next-line no-console
      console.log(`Complete.`);
    },
    err => {
      // eslint-disable-next-line no-console
      console.log(err);
    }
  )
  .then(() => {
    process.exit();
  });
