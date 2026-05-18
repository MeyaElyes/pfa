import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-progress-bar',
  templateUrl: './progress-bar.component.html',
  styleUrls: ['./progress-bar.component.css']
})
export class ProgressBarComponent {
  @Input() value = 0; // 0..100

  get clamped(): number {
    return Math.max(0, Math.min(100, this.value));
  }

  get color(): string {
    if (this.clamped < 10)  return 'var(--color-critical)';
    if (this.clamped < 20)  return 'var(--color-warn)';
    return 'var(--color-ok)';
  }
}
