If CI fails:

1. Read workflow logs
2. Fix ONLY failing issue
3. Do not refactor working code
4. Keep dependency versions
5. Ensure bun run test and pytest pass
6. Ensure vite build succeeds
7. Commit minimal fix
