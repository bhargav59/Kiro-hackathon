// Utility to generate thumbnails based on content
export const generateThumbnail = (title: string) => {
  const colors = {
    'Docker': { primary: '#2496ED', secondary: '#1E88E5', accent: '#0D47A1' },
    'Kubernetes': { primary: '#326CE5', secondary: '#1976D2', accent: '#0D47A1' },
    'Terraform': { primary: '#7B42BC', secondary: '#673AB7', accent: '#4527A0' },
    'Jenkins': { primary: '#D33833', secondary: '#C62828', accent: '#B71C1C' },
    'Prometheus': { primary: '#E6522C', secondary: '#FF5722', accent: '#D84315' },
    'GraphQL': { primary: '#E10098', secondary: '#C2185B', accent: '#AD1457' },
    'Redis': { primary: '#DC382D', secondary: '#D32F2F', accent: '#C62828' },
    'AWS': { primary: '#FF9900', secondary: '#FF8F00', accent: '#E65100' },
    'MongoDB': { primary: '#47A248', secondary: '#388E3C', accent: '#2E7D32' },
    'React': { primary: '#61DAFB', secondary: '#29B6F6', accent: '#0288D1' },
    'default': { primary: '#6366F1', secondary: '#5B21B6', accent: '#4338CA' }
  };

  const patterns = {
    'Docker': `
      <circle cx="50" cy="50" r="8" fill="white" opacity="0.3"/>
      <circle cx="80" cy="50" r="8" fill="white" opacity="0.3"/>
      <circle cx="110" cy="50" r="8" fill="white" opacity="0.3"/>
      <circle cx="65" cy="30" r="8" fill="white" opacity="0.3"/>
      <circle cx="95" cy="30" r="8" fill="white" opacity="0.3"/>
      <rect x="40" y="40" width="80" height="20" rx="10" fill="white" opacity="0.4"/>
    `,
    'Kubernetes': `
      <polygon points="150,30 180,60 150,90 120,60" fill="white" opacity="0.3"/>
      <circle cx="150" cy="60" r="15" fill="white" opacity="0.4"/>
      <circle cx="120" cy="40" r="6" fill="white" opacity="0.3"/>
      <circle cx="180" cy="40" r="6" fill="white" opacity="0.3"/>
      <circle cx="120" cy="80" r="6" fill="white" opacity="0.3"/>
      <circle cx="180" cy="80" r="6" fill="white" opacity="0.3"/>
    `,
    'React': `
      <ellipse cx="150" cy="100" rx="60" ry="20" fill="none" stroke="white" stroke-width="3" opacity="0.4"/>
      <ellipse cx="150" cy="100" rx="60" ry="20" fill="none" stroke="white" stroke-width="3" opacity="0.4" transform="rotate(60 150 100)"/>
      <ellipse cx="150" cy="100" rx="60" ry="20" fill="none" stroke="white" stroke-width="3" opacity="0.4" transform="rotate(-60 150 100)"/>
      <circle cx="150" cy="100" r="8" fill="white"/>
    `,
    'AWS': `
      <path d="M50 80 Q80 60 110 80 Q140 60 170 80 Q200 60 230 80" stroke="white" stroke-width="3" fill="none" opacity="0.4"/>
      <path d="M60 90 Q90 70 120 90 Q150 70 180 90 Q210 70 240 90" stroke="white" stroke-width="3" fill="none" opacity="0.3"/>
      <circle cx="80" cy="70" r="4" fill="white" opacity="0.6"/>
      <circle cx="150" cy="70" r="4" fill="white" opacity="0.6"/>
      <circle cx="220" cy="70" r="4" fill="white" opacity="0.6"/>
    `,
    'default': `
      <rect x="60" y="60" width="40" height="40" rx="8" fill="white" opacity="0.3"/>
      <rect x="120" y="60" width="40" height="40" rx="8" fill="white" opacity="0.3"/>
      <rect x="180" y="60" width="40" height="40" rx="8" fill="white" opacity="0.3"/>
      <rect x="90" y="100" width="40" height="40" rx="8" fill="white" opacity="0.4"/>
      <rect x="150" y="100" width="40" height="40" rx="8" fill="white" opacity="0.4"/>
    `
  };

  const getColorScheme = (title: string) => {
    for (const [key, scheme] of Object.entries(colors)) {
      if (title.toLowerCase().includes(key.toLowerCase())) {
        return scheme;
      }
    }
    return colors.default;
  };

  const getPattern = (title: string) => {
    for (const [key, pattern] of Object.entries(patterns)) {
      if (title.toLowerCase().includes(key.toLowerCase())) {
        return pattern;
      }
    }
    return patterns.default;
  };

  const colorScheme = getColorScheme(title);
  const pattern = getPattern(title);
  const initials = title.split(' ').slice(0, 2).map(word => word[0]).join('').toUpperCase();

  const svg = `
    <svg width="400" height="250" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="mainGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${colorScheme.primary};stop-opacity:1" />
          <stop offset="50%" style="stop-color:${colorScheme.secondary};stop-opacity:1" />
          <stop offset="100%" style="stop-color:${colorScheme.accent};stop-opacity:1" />
        </linearGradient>
        <linearGradient id="overlayGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:rgba(255,255,255,0.1);stop-opacity:1" />
          <stop offset="100%" style="stop-color:rgba(0,0,0,0.1);stop-opacity:1" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <!-- Background -->
      <rect width="400" height="250" fill="url(#mainGrad)" rx="12"/>
      <rect width="400" height="250" fill="url(#overlayGrad)" rx="12"/>
      
      <!-- Pattern -->
      <g opacity="0.6">
        ${pattern}
      </g>
      
      <!-- Main Content -->
      <g filter="url(#glow)">
        <text x="200" y="120" font-family="Arial, sans-serif" font-size="48" font-weight="bold" 
              text-anchor="middle" fill="white" opacity="0.95">${initials}</text>
      </g>
      
      <!-- Labels -->
      <rect x="20" y="200" width="120" height="30" rx="15" fill="rgba(255,255,255,0.2)" opacity="0.9"/>
      <text x="80" y="220" font-family="Arial, sans-serif" font-size="12" font-weight="600" 
            text-anchor="middle" fill="white">TECH GUIDE</text>
      
      <rect x="260" y="200" width="120" height="30" rx="15" fill="rgba(255,255,255,0.15)" opacity="0.9"/>
      <text x="320" y="220" font-family="Arial, sans-serif" font-size="12" font-weight="500" 
            text-anchor="middle" fill="white">INSTALLATION</text>
            
      <!-- Decorative elements -->
      <circle cx="350" cy="50" r="20" fill="rgba(255,255,255,0.1)" opacity="0.8"/>
      <circle cx="50" cy="50" r="15" fill="rgba(255,255,255,0.1)" opacity="0.6"/>
      <circle cx="350" cy="200" r="10" fill="rgba(255,255,255,0.1)" opacity="0.7"/>
    </svg>
  `;

  return `data:image/svg+xml;base64,${btoa(svg)}`;
};

export const getTechIcon = (title: string) => {
  const icons = {
    'docker': '🐳',
    'kubernetes': '☸️',
    'terraform': '🏗️',
    'jenkins': '🔧',
    'prometheus': '📊',
    'graphql': '🔗',
    'redis': '🔴',
    'aws': '☁️',
    'mongodb': '🍃',
    'react': '⚛️'
  };

  for (const [key, icon] of Object.entries(icons)) {
    if (title.toLowerCase().includes(key)) {
      return icon;
    }
  }
  return '📚';
};
