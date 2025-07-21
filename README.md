# Behavioral Data Science Research Lab Website

A cyberpunk-themed 90s retro website for the Behavioral Data Science Research Lab. Built with pure HTML, CSS, and JavaScript for easy deployment and maintenance.

## 🎨 Features

- **Cyberpunk 90s Retro Design**: Neon colors, pixel art, glitch effects
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Animated Elements**: Pixel art animations, glitch effects, matrix rain
- **Interactive Forms**: Contact and application forms with cyberpunk styling
- **Easy to Customize**: Simple structure for content updates

## 📁 File Structure

```
bds-lab-website/
├── index.html          # Homepage
├── about.html          # About Us page
├── news.html           # News page
├── projects.html       # Current Projects page
├── publications.html   # Publications page
├── apply.html          # Apply page
├── contact.html        # Contact page
├── styles.css          # All CSS styling
├── script.js           # Interactive JavaScript effects
└── README.md           # This file
```

## 🚀 Quick Start

1. **Clone or Download** the files to your local machine
2. **Open `index.html`** in your web browser to preview locally
3. **Customize Content** by editing the HTML files
4. **Deploy** to your web server or GitHub Pages

## 🎯 Content Customization

### Homepage (`index.html`)
- Update the hero section text
- Modify the feature cards with your lab's specialties
- Change the pixel art logo pattern

### About Page (`about.html`)
- Add your lab director's information
- List current lab members
- Describe your research focus and facilities

### News Page (`news.html`)
- Replace placeholder news items with actual announcements
- Add dates and links to full articles

### Projects Page (`projects.html`)
- Add your current research projects
- Include funding sources and team information

### Publications Page (`publications.html`)
- List your lab's publications from the past 3 years
- Add DOI links and PDF downloads

### Apply Page (`apply.html`)
- Customize the application form fields
- Add specific requirements for your lab

### Contact Page (`contact.html`)
- Add your lab's actual contact information
- Update office hours and location

## 🌐 Deployment Options

### Option 1: GitHub Pages (Recommended)

1. **Create a GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/bds-lab-website.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Click "Settings" → "Pages"
   - Select "Deploy from a branch"
   - Choose "main" branch and "/ (root)" folder
   - Click "Save"

3. **Custom Domain Setup**
   - In GitHub Pages settings, add your domain: `behavioral-data-science.org`
   - Create a `CNAME` file in your repository with:
     ```
     behavioral-data-science.org
     ```
   - Update your domain's DNS settings to point to GitHub Pages

### Option 2: Traditional Web Hosting

1. **Upload Files** to your web server via FTP/SFTP
2. **Point Domain** to your hosting provider
3. **Test** all pages and forms

### Option 3: Netlify/Vercel

1. **Connect Repository** to Netlify or Vercel
2. **Deploy** automatically from your Git repository
3. **Add Custom Domain** in the hosting platform settings

## 🎨 Customization Guide

### Colors
Edit the CSS variables in `styles.css`:
```css
:root {
    --neon-cyan: #00ffff;
    --neon-pink: #ff00ff;
    --neon-green: #00ff00;
    --neon-yellow: #ffff00;
    /* ... */
}
```

### Fonts
The site uses Google Fonts:
- **Orbitron**: For headings and titles
- **VT323**: For body text and monospace elements

### Animations
Modify animation speeds and effects in `script.js`:
- Grid movement speed
- Glitch effect intensity
- Pixel animation timing

## 📱 Mobile Optimization

The website is fully responsive with:
- Mobile-first design approach
- Touch-friendly navigation
- Optimized forms for mobile input
- Readable text at all screen sizes

## 🔧 Technical Details

- **No Dependencies**: Pure HTML/CSS/JavaScript
- **Fast Loading**: Optimized for performance
- **SEO Friendly**: Semantic HTML structure
- **Accessible**: Proper ARIA labels and keyboard navigation
- **Cross-Browser**: Works in all modern browsers

## 📞 Support

For questions about:
- **Content Updates**: Edit the HTML files directly
- **Styling Changes**: Modify `styles.css`
- **Interactive Features**: Update `script.js`
- **Deployment Issues**: Check your hosting provider's documentation

## 🎯 Next Steps

1. **Add Your Content**: Replace all placeholder text with your lab's information
2. **Upload Images**: Add lab photos, member pictures, and research images
3. **Set Up Forms**: Configure form handling for contact and application forms
4. **Add Analytics**: Include Google Analytics or other tracking
5. **SEO Optimization**: Add meta tags and descriptions for better search visibility

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for the Behavioral Data Science Research Lab** 