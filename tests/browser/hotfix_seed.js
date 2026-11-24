// 8.39.1 fixture, from the owner's description of Nov 23 (no real backup was available).
// Arnold plan. Plan week 6 (index 5). Weeks 1 to 5 logged in full, each on its own calendar week.
// Week 6, last calendar week (Nov 16 to 22):
//   Mon slot Chest and Back: logged partly on Fri Nov 20 with Short applied.
//   Tue slot Arms: logged partly on Tue Nov 17.
//   Fri slot Chest (chest-b): logged partly on Thu Nov 19.
//   Sat slot Arms (arms-b): logged in full on Sat Nov 21.
// Nothing logged on Mon Nov 23. Run inside the page before a reload.
() => {
  setSplit('arnold');
  const s = {}, key = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  const r5 = n => Math.round(n / 5) * 5, week = activeSplit().week;
  const put = (ex, wk, d, frac) => {
    const wt = r5(40 + (ex.maxPct || 0.5) * 100 + wk * 5), r = ex.repRange[0];
    const e = { d, week: wk, day: null, weight: wt, reps: r, s1: { w: wt, r }, failure: null, variant: activeVariant(ex) };
    if (frac === 1) e.s2 = { w: wt, r };
    (s[ex.id] = s[ex.id] || []).push(e);
    return e;
  };
  const logDay = (day, wk, d, n, oneSet) => { const list = splitDayExercises(day); list.slice(0, n == null ? list.length : n).forEach(ex => { put(ex, wk, d, oneSet ? 0 : 1).day = day; }); return list.length; };
  // Weeks 1 to 5: Mon Oct 19 is week 1.
  for (let w = 0; w < 5; w++) week.forEach((day, i) => { if (day !== 'rest') logDay(day, w, key(new Date(2026, 9, 19 + w * 7 + i))); });
  // Week 6, last calendar week. Short on the Monday slot, chosen on Fri Nov 20.
  shortDays['5|chest'] = true; persistLifeHappens();
  logDay('chest', 5, '2026-11-20', 3, true);
  logDay('arms', 5, '2026-11-17', 2, true);
  logDay('chest-b', 5, '2026-11-19', 3, true);
  logDay('arms-b', 5, '2026-11-21');
  localStorage.setItem('monk_sessions_v1', JSON.stringify(s));
  localStorage.setItem('monk_mode_train_week_v1', '5');
  localStorage.setItem('monk_day_mode', JSON.stringify({ date: '2026-11-20', week: 5, day: 'chest', mode: 'short', min: null }));
  localStorage.setItem('monk_mode_maxes_v1', JSON.stringify({ squat: 275, bench: 205, ohp: 95 }));
  return Object.keys(s).length;
}
