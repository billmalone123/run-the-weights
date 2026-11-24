// 8.38 fixture: a block of logs on the 4 day plan. Run with evaluate(BLOCK_SEED, opts).
// opts: weeks (how many weeks have logs, from week 1), lastWeek (the week the app sits on, 0 based),
// maxes (stored), base (the maxes the logged weights grow from, default maxes), and bump {exId: [week, weight, reps]} to plant one set.
(o) => {
  setSplit('upper-lower');
  const weeks = o.weeks == null ? 10 : o.weeks, last = o.lastWeek == null ? 9 : o.lastWeek, mx = o.maxes || { squat: 300, bench: 225, ohp: 60 };
  const bm = o.base || mx, r5 = n => Math.round(n / 5) * 5, s = {}, split = activeSplit().week;
  const mon = new Date(2026, 10, 16 - last * 7 - 7 * (o.shift || 0));   // shift: weeks earlier on the calendar
  const key = dd => dd.getFullYear() + '-' + String(dd.getMonth() + 1).padStart(2, '0') + '-' + String(dd.getDate()).padStart(2, '0');
  for (let w = 0; w < 10; w++) {
    if (o.only ? o.only.indexOf(w) === -1 : w >= weeks) continue;
    split.forEach((day, i) => {
      if (day === 'rest' || (SPLIT_DAYS[day] || {}).rest) return;
      splitDayExercises(day).forEach(ex => {
        const base = ex.maxKey && ex.maxPct && bm[ex.maxKey] ? r5(bm[ex.maxKey] * ex.maxPct) : 50;
        const climb = w - Math.floor((w + 1) / 4), wt = (w % 4 === 3) ? r5(base * Math.pow(1.03, climb) * 0.85) : r5(base * Math.pow(1.03, climb));
        const r = ex.repRange[0], d = key(new Date(mon.getFullYear(), mon.getMonth(), mon.getDate() + w * 7 + i));
        (s[ex.id] = s[ex.id] || []).push({ d, week: w, day, weight: wt, reps: r, s1: { w: wt, r }, s2: { w: wt, r }, failure: null, variant: activeVariant(ex) });
      });
    });
  }
  Object.keys(o.bump || {}).forEach(id => { const b = o.bump[id], e = (s[id] || []).filter(x => x.week === b[0])[0]; if (e) { e.weight = b[1]; e.reps = b[2]; e.s1 = { w: b[1], r: b[2] }; } });
  localStorage.setItem('monk_sessions_v1', JSON.stringify(s));
  localStorage.setItem('monk_mode_maxes_v1', JSON.stringify(mx));
  localStorage.setItem('monk_mode_train_week_v1', String(last));
  return Object.keys(s).length;
}
