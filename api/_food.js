// 8.32: the server half of the Food lock. Files in api/ that start with an
// underscore are not routes on Vercel, so this is only ever required.
// Keep this in step with FOOD_ENABLED in index.html: turning Food back on
// means setting both to true.
module.exports = { FOOD_ENABLED: false };
