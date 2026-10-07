/** Precompiled Tailwind build; replaces the runtime CDN compiler.
 *  Rebuild with: npx tailwindcss@3.4.17 -i tailwind.input.css -o static/css/tailwind.css --minify
 */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./menu/templates/**/*.html",
    "./order/templates/**/*.html",
    "./user/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#fff7ed",
          100: "#ffedd5",
          500: "#f97316",
          600: "#ea580c",
          700: "#c2410c",
        },
      },
      boxShadow: {
        soft: "0 20px 50px -24px rgba(15, 23, 42, 0.28)",
      },
    },
  },
};
