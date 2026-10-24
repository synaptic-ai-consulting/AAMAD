# Reachable states

Specify every state a user can actually reach. "Make it responsive" or "handle errors" is not a state matrix.

## Baseline states

| State | What the user must still understand | Typical failure if omitted |
|---|---|---|
| Loading | Which task is in progress and that the system has accepted the request | Blank screen; double submit |
| Empty | What is missing and the next useful action | Fake data or a dead page |
| Populated | Primary task and hierarchy | Dashboard chrome with no action |
| Validation | Which fields failed and how to fix them | Lost input; generic "invalid" |
| Error | What happened and a useful next step | Retry loops with no explanation |
| Permission | Why access is denied and who can grant it | Silent hide or a dead control |
| Unavailable | That the control exists but cannot run now | Clicking a stub as if it worked |

Every interactive control must work or clearly disclose its unavailable state. Forms must retain recoverable user input after a failed submission. Destructive actions need an appropriate confirmation or recovery path.

## Agent and runtime states

When the product involves agents or long-running model work, specify these where they exist:

| State | User-visible meaning |
|---|---|
| Running | Work is executing; distinguish from a completed result |
| Waiting-for-input | The system needs the user before it can continue |
| Approval-required | A proposed action is waiting; it has not executed |
| Failed | The run stopped; say what failed and what the user can do |
| Cancelled | The user or system stopped the run |
| Partial | Some steps finished; show what is done vs still open |

The interface must distinguish a **proposed** action from an action that **actually executed**.

Do not invent agent states the SAD does not include. If the SAD has no model call, omit this table.

## Responsive behavior

For each primary screen, say what changes at the agreed viewports (not merely "make responsive"):

- What stacks, hides, or moves
- What stays persistent (primary action, status, errors)
- How dense tables, long labels, and empty results behave

Record the viewport list in `ux.md` and reuse it in `ux-review.md`.
