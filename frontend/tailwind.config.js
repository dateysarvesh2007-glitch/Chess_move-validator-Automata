module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Soft pastel palette based on color theory for accessibility and contrast
        primary: "#6C63FF", // muted violet (high contrast on dark backgrounds)
        secondary: "#F0F4EF", // off‑white, gentle on eyes
        accent: "#FFD166", // warm gold accent
        success: "#88D498", // soothing green for accepted moves
        danger: "#F28B82", // soft red for rejections
        background: "#1E2A38", // dark navy base
      },
      borderRadius: {
        lg: "0.75rem",
      },
      boxShadow: {
        card: "0 4px 6px rgba(0,0,0,0.1)"
      }
    }
  },
  plugins: []
};