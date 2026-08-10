# SQL and Rust Foundations Practice Contract

This is the canonical StudySyndicate practice contract for **resume-visible software skill claims**.

The immediate priority is SQL because it is both central to active projects and common in target job descriptions. Rust is the secondary deep-practice lane. Other technologies already shown publicly are maintained through smaller claim-defense reviews instead of receiving equal study time.

## Claim-defense doctrine

A skill label on a public website is not evidence by itself.

A claim reaches **defensible** only when the learner can:

1. reconstruct the named foundation without AI assistance;
2. explain why the solution works and what common failure looks like;
3. complete the track mastery gates;
4. use AI afterward for critique, alternatives, or deeper review rather than as the first source of the solution.

The machine-readable contract uses three states:

`exposed -> practicing -> defensible`

Percentages or visual confidence meters must not be treated as percentile rank or expert certification.

## Time allocation

Until intentionally revised:

- **SQL: 50%**
- **Rust: 25%**
- **maintenance of other public claims: 25%**

A normal session is 45-60 minutes. Every session must contain typed retrieval, query writing, code, or explanation from memory. Reading alone does not count as practice.

## SQL track

SQL is the primary lane. Work from relational reasoning outward rather than memorizing isolated syntax.

### 1. SELECT, filtering, and ordering

Be able to write from memory:

- `SELECT`, `FROM`, `WHERE`
- `ORDER BY`, `LIMIT`
- `DISTINCT`

Practice goal: explain why each returned row is present.

### 2. Aggregation and grouped reasoning

Be able to use and explain:

- `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
- `GROUP BY`
- `HAVING`

Foundation gate: explain that `WHERE` filters rows before grouping while `HAVING` filters groups after aggregation.

### 3. Joins and cardinality

Be able to use:

- `INNER JOIN`
- `LEFT JOIN`

Do not stop at syntax. Diagnose one-to-many and many-to-many row multiplication, know why duplicate-looking rows appear, and know when preserving unmatched left-side rows is required.

### 4. NULL

Be comfortable with:

- `IS NULL`
- `IS NOT NULL`
- `COALESCE`
- the fact that `NULL = NULL` is not true

Treat NULL behavior as part of the relational model, not an edge-case trivia question.

### 5. Subqueries and CTEs

Practice:

- scalar and set subqueries
- correlated subqueries
- `WITH` common table expressions

Prefer clarity over nesting cleverness.

### 6. Window functions

Practice until these are ordinary tools:

- `ROW_NUMBER()`
- `RANK()` / `DENSE_RANK()`
- `LAG()` / `LEAD()`
- aggregate windows such as `SUM(...) OVER (...)`
- `PARTITION BY`

A core drill is “latest event per task,” because it forces partitioning, ordering, and row selection.

### 7. Safe data changes

Practice:

- `INSERT`
- `UPDATE`
- `DELETE`
- transactions
- rollback paths

Never treat a successful `UPDATE` as sufficient proof if the intended row set was not first bounded and inspected.

### 8. Relational modeling

Be able to design and explain:

- primary keys
- foreign keys
- one-to-many and many-to-many relationships
- bridge tables
- uniqueness and check constraints
- normalization versus deliberate denormalization

### 9. Indexes and query plans

Be able to answer:

- why an index may speed reads;
- why the same index may slow writes;
- why column order matters in a composite index;
- what a query plan is telling you at a basic level;
- when low selectivity or tiny tables make an index less useful.

### 10. SQL graduation gate

Given an unfamiliar schema, without AI assistance:

1. inspect relationships;
2. write a multi-table join;
3. aggregate correctly;
4. diagnose duplicate-row cardinality;
5. use a CTE;
6. use a window function;
7. handle NULL deliberately;
8. modify data safely in a transaction;
9. design a normalized relationship;
10. recommend an index and explain its tradeoffs.

## Rust track

Rust is learned foundation-first. Do not skip ownership and borrowing to chase framework-sized projects.

### Foundation order

1. bindings, scalar types, functions, and expressions
2. structs, enums, and pattern matching
3. ownership and moves
4. borrowing, references, mutable references, and slices
5. `Option<T>` and `Result<T, E>`
6. collections and iterators
7. traits and generics
8. modules and tests
9. lifetime reasoning
10. concurrency foundations

### Ownership gate

Be able to explain why this moves the `String`:

```rust
let s1 = String::from("hello");
let s2 = s1;
// println!("{s1}"); // invalid: value moved
```

Then repair the design with borrowing when ownership transfer is unnecessary rather than reflexively calling `clone()`.

### Error-handling gate

Prefer typed failure:

- `Option<T>` for absence
- `Result<T, E>` for recoverable failure
- `?` for propagation when the caller owns the decision

Panic-driven control flow does not satisfy the foundation gate.

### Testing gate

Every nontrivial Rust exercise should have a runnable `cargo test` path once it becomes a file/project rather than a whiteboard drill.

## Integration project: taskq

The first serious project is intentionally small:

```text
taskq add "Fix deployment validator"
taskq list
taskq done 12
taskq show 12
```

Build it in four phases:

1. **Rust core** — argument parsing, `Task`, `TaskStatus`, `Result`-based errors, unit tests.
2. **SQLite storage** — normalized schema, CRUD, foreign keys, transactional status changes.
3. **Analytical SQL** — open-task aggregation, latest-event window query, repository ranking.
4. **Defensibility review** — reconstruct core pieces without AI, explain the SQL, explain ownership/borrowing, and retain `cargo test` evidence.

This project exists to make the SQL and Rust tracks collide productively instead of becoming two disconnected tutorial streams.

## Maintenance lane for other public claims

Use the remaining 25% to rotate through technologies already shown publicly:

- Python
- JavaScript
- TypeScript
- Pandas
- NumPy
- Matplotlib
- React
- Django
- Flask
- Node.js
- Java
- C

Maintenance does **not** mean building eleven parallel curricula. For each technology, keep one small claim-defense packet:

- one foundation explanation from memory;
- one small code/query exercise;
- one debugging or “why did this fail?” exercise;
- one note describing what is practiced versus what still requires reference material.

If a public claim cannot pass that packet, mark it `practicing` rather than pretending the visualization is proof of mastery.

## Weekly cadence

| Day | Focus |
| --- | --- |
| Monday | SQL foundations and retrieval practice |
| Tuesday | Rust foundations |
| Wednesday | SQL joins, aggregation, and schema reasoning |
| Thursday | Rust foundations |
| Friday | SQL advanced query challenge |
| Weekend | 60-90 minute `taskq` integration sprint |

Normal 55-minute session:

1. 10 minutes closed-book review;
2. 25 minutes typed exercises;
3. 15 minutes building or repairing something;
4. 5 minutes recording confusion and the next retrieval target.

## Machine-readable pack

The canonical exercise and mastery contract lives at:

`content/software/sql-rust-foundations.v1.json`

It contains:

- 10 SQL modules and 15 SQL exercises;
- 10 Rust modules and 10 Rust exercises;
- mastery gates for both tracks;
- the `taskq` integration project;
- time allocation, weekly cadence, session structure, and claim-defense policy.

## Validation

Run:

```bash
python scripts/validate-software-foundations.py
```

The validator checks schema identity, allocation math, required module ordering, exercise references, unique identifiers, required mastery language, integration-project phases, maintenance claims, cadence, session time, acceptance criteria, and synchronization between this doctrine and the machine-readable pack.
