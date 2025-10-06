import * as cheerio from 'cheerio';
import pdfParse from 'pdf-parse';

interface InjuryReport {
  player: string;
  team: string;
  status: string;
  reason: string;
  date: string;
}

export class InjuryReportScraper {
  private baseUrl = 'https://official.nba.com/nba-injury-report-2024-25-season/';

  private async fetchPage(): Promise<string> {
    const response = await fetch(this.baseUrl, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch injury report page: ${response.status} ${response.statusText}`);
    }

    return response.text();
  }

  private async fetchPDF(url: string): Promise<Buffer> {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch PDF: ${response.status} ${response.statusText}`);
    }

    return Buffer.from(await response.arrayBuffer());
  }

  private async getLatestPDFUrl(): Promise<string> {
    const html = await this.fetchPage();
    const $ = cheerio.load(html);
    
    // Find the latest PDF link - usually the first one in the content
    const pdfLink = $('a[href$=".pdf"]').first().attr('href');
    
    if (!pdfLink) {
      throw new Error('No PDF link found on the injury report page');
    }

    return pdfLink;
  }

  private parsePDFContent(text: string): InjuryReport[] {
    const lines = text.split('\n');
    const reports: InjuryReport[] = [];
    let currentTeam = '';

    for (const line of lines) {
      // Skip empty lines and headers
      if (!line.trim() || line.includes('Game Date') || line.includes('Page')) {
        continue;
      }

      // Team name lines are usually in all caps
      if (line.toUpperCase() === line && !line.includes('-')) {
        currentTeam = line.trim();
        continue;
      }

      // Try to parse player injury line
      const parts = line.split('-').map(p => p.trim());
      if (parts.length >= 2) {
        const [player, statusAndReason] = parts;
        const [status, ...reasonParts] = statusAndReason.split(' ');
        
        reports.push({
          player: player.trim(),
          team: currentTeam,
          status: status.trim(),
          reason: reasonParts.join(' ').trim(),
          date: new Date().toISOString().split('T')[0], // Current date
        });
      }
    }

    return reports;
  }

  async getLatestInjuries(): Promise<InjuryReport[]> {
    try {
      const pdfUrl = await this.getLatestPDFUrl();
      const pdfBuffer = await this.fetchPDF(pdfUrl);
      const data = await pdfParse(pdfBuffer);
      
      return this.parsePDFContent(data.text);
    } catch (error) {
      console.error('Error fetching injury report:', error);
      throw error;
    }
  }

  async getPlayerStatus(playerName: string): Promise<InjuryReport | null> {
    const injuries = await this.getLatestInjuries();
    return injuries.find(injury => 
      injury.player.toLowerCase().includes(playerName.toLowerCase())
    ) || null;
  }
}

// Create a singleton instance
export const injuryReporter = new InjuryReportScraper();
