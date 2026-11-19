// Seed data for the browser checks: a plan follower mid week with logged
// lifts, runs, food and one weigh in. Run inside the page with evaluate().
() => {
  // Six weeks of logs (weeks 0-5) for every exercise in the 4 day plan, then sit on week 6.
  setSplit('upper-lower');
  const ids = [];
  activeSplit().week.forEach(d => { if (d !== 'rest' && !(SPLIT_DAYS[d] || {}).rest) splitDayExercises(d).forEach(ex => { if (ids.indexOf(ex.id) === -1) ids.push(ex.id); }); });
  const s = {};
  ids.forEach((id, i) => {
    const base = 40 + i * 10;
    s[id] = [];
    for (let w = 0; w < 6; w++) {
      const wt = base + w * 5, dd = new Date(2026, 9, 5 + w * 7);
      const d = dd.getFullYear() + '-' + String(dd.getMonth() + 1).padStart(2, '0') + '-' + String(dd.getDate()).padStart(2, '0');
      s[id].push({ d, week: w, weight: wt, reps: 8, s1: { w: wt, r: 8 }, s2: { w: wt, r: 8 }, failure: null, variant: activeVariant(EX_BY_ID[id]) });
    }
  });
  localStorage.setItem('monk_sessions_v1', JSON.stringify(s));
  localStorage.setItem('monk_mode_train_week_v1', '6');
  return ids.length;
}
