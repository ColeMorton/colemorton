
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  try {
    const page = await browser.newPage();

    // Set viewport and device scale factor
    await page.setViewport({
      width: 1920,
      height: 1080,
      deviceScaleFactor: 2
    });

    // Navigate to the page
    console.log('Navigating to:', 'http://localhost:4321/photo-booth?dashboard=logo_generation&mode=dark&aspect_ratio=16:9');
    await page.goto('http://localhost:4321/photo-booth?dashboard=logo_generation&mode=dark&aspect_ratio=16:9', { waitUntil: 'networkidle0', timeout: 30000 });

    // Wait for dashboard to be ready
    console.log('Waiting for dashboard to be ready...');
    await page.waitForSelector('.photo-booth-ready', { timeout: 30000 });

    /* Wait for all charts to be fully loaded and rendered */
    console.log('Waiting for charts to load and render...');
    try {
      /* Wait for all PlotlyChart containers to be present */
      await page.waitForFunction(() => {
        const chartContainers = document.querySelectorAll('[data-testid="plotly-chart-container"]');
        if (chartContainers.length === 0) {
          console.log('No chart containers found, continuing...');
          return true; /* No charts present, continue */
        }

        let allChartsReady = true;
        let readyCount = 0;

        chartContainers.forEach((container, index) => {
          const isLoaded = container.getAttribute('data-chart-loaded') === 'true';
          const isRendered = container.getAttribute('data-chart-rendered') === 'true';
          const isReady = isLoaded && isRendered;

          console.log(`Chart ${index}: loaded=${isLoaded}, rendered=${isRendered}, ready=${isReady}`);

          if (isReady) {
            readyCount++;
          } else {
            allChartsReady = false;
          }
        });

        console.log(`Charts ready: ${readyCount}/${chartContainers.length}`);
        return allChartsReady;
      }, { timeout: 15000 });

      console.log('All charts are loaded and rendered!');

      /* Additional short wait to ensure visual stability */
      await new Promise(resolve => setTimeout(resolve, 1000));

    } catch (error) {
      console.warn('Chart loading timeout, continuing with screenshot:', error.message);
      /* Fallback: short wait if chart detection fails */
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    // Hide UI elements for clean screenshot
    console.log('Hiding UI elements for clean screenshot...');
    await page.evaluate(() => {
      // Hide photo booth controls
      const controls = document.querySelectorAll('.photo-booth-controls');
      controls.forEach(element => {
        element.style.display = 'none';
        element.style.visibility = 'hidden';
      });

      // Hide Astro dev toolbar
      const devToolbarSelectors = [
        'astro-dev-toolbar',
        '#dev-toolbar-root',
        '[data-astro-dev-toolbar]',
        '.astro-dev-toolbar',
        '#astro-dev-toolbar'
      ];

      let hiddenDevElements = 0;
      devToolbarSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          element.style.display = 'none';
          element.style.visibility = 'hidden';
          hiddenDevElements++;
        });
      });

      console.log(`Hidden ${controls.length} control elements and ${hiddenDevElements} dev toolbar elements`);
    });

    // Take screenshot
    console.log('Taking screenshot...');
    await page.screenshot({
      path: '/Users/colemorton/Projects/colemorton/data/outputs/photo-booth/logo_generation_dark_16x9_png_150dpi_attribution_20250914_134745_temp.png',
      fullPage: false,
      type: 'png',
      quality: undefined
    });

    console.log('Screenshot saved to:', '/Users/colemorton/Projects/colemorton/data/outputs/photo-booth/logo_generation_dark_16x9_png_150dpi_attribution_20250914_134745_temp.png');

  } catch (error) {
    console.error('Screenshot generation failed:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
