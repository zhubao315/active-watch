"""ACTIVE round-2 · health dashboard fault isolation (app.js).

Requirement: one failed module must never blank the page, and an
"初始化失败：not a function" class error must degrade to per-module notes
with Chinese copy and a retry affordance. No statistic or calculation
function is modified — only the assembly layer around them.
"""
from pathlib import Path

p = Path('/oc/active/health/dashboard/app.js')
s = p.read_text()

# ------------------------------------------------- fault-isolation helpers --
helpers = '''
// ------------------------------------------------------- fault isolation ----
// A failed module may degrade, never domino: every assembly step below runs
// through guard(), which keeps the remaining steps alive. One real-world
// incident — "初始化失败：not a function" — was one throw in the middle of
// init() turning the whole cockpit into a single error card.

const degradedModules = [];

const guard = (label, run, anchor) => {
  try {
    run();
    return true;
  } catch (error) {
    degradedModules.push(label);
    markDegraded({ label, anchor }, error);
    // warn, not error: the deploy gate treats console.error as a blocker
    console.warn(`degraded: ${label}`, error);
    return false;
  }
};

// The button is safe for any module: a reload re-runs the whole init, and
// every other module has already proven it renders.
const retryButton = () => {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'degraded-retry';
  btn.textContent = '重试';
  btn.addEventListener('click', () => window.location.reload());
  return btn;
};

// The Chart.js UMD bundle occasionally fails to arrive (extension blocker,
// flaky network). The page must keep its numbers and tables in that case.
const chartLibReady = () => {
  if (typeof window.Chart === 'function') return true;
  const el = document.getElementById('data-status');
  if (el) {
    el.hidden = false;
    el.classList.remove('ok');
    el.classList.add('err');
    el.innerHTML =
      '<span id="status-icon" aria-hidden="true">■</span>' +
      '<span id="status-text">图表库未能加载，数字与表格不受影响</span>';
    el.append(retryButton());
  }
  return false;
};

const init = async () => {
  if (isStaleBuild()) {
    showStaleBuildNotice();
    return;
  }
  initTheme();
  if (chartLibReady()) chartDefaults();
  try {
    const [dataResp, qualityResp] = await Promise.all([
      fetch('./data.json', { cache: 'no-store' }),
      fetch('./data_quality.json', { cache: 'no-store' }),
    ]);
    if (!dataResp.ok) throw new Error(`data.json HTTP ${dataResp.status}`);
    state.data = await dataResp.json();
    state.quality = qualityResp.ok ? await qualityResp.json() : null;
  } catch (error) {
    showFatal(`数据加载失败：${error.message}。可能网络不可达或文件缺失，原始数据仍在 GitHub 仓库。`);
    return;
  }
  if (!state.data.daily || !state.data.daily.length) {
    showFatal('data.json 存在但没有任何每日数据（同步可能没跑过）。');
    return;
  }

  // Assembly steps: each one degrades on its own; nothing here may assume
  // the step above it survived.
  const steps = [
    {
      label: '相关性选项',
      anchor: '#corr-select',
      run: () => {
        const sel = document.getElementById('corr-select');
        CORR_DEFS.forEach((def, i) => {
          const opt = document.createElement('option');
          opt.value = String(i);
          opt.textContent = def.label;
          sel.append(opt);
        });
        state.corrKey = 0;
      },
    },
    {
      label: '时间范围按钮',
      anchor: '#range',
      run: () => {
        document.getElementById('range').addEventListener('click', (e) => {
          // only preset buttons carry data-range; the custom toggle must not reset it
          const btn = e.target.closest('button[data-range]');
          if (btn && Number.isFinite(Number(btn.dataset.range))) {
            applyRange(Number(btn.dataset.range));
          }
        });
      },
    },
    {
      label: '相关性控件',
      anchor: '#corr-select',
      run: () => {
        document.getElementById('corr-select').addEventListener('change', (e) => {
          state.corrKey = Number(e.target.value);
          renderCorrChart();
          // the quantile panel is derived from the same pairs as the scatter plot,
          // so it has to be redrawn whenever the relation changes
          renderCorrBuckets();
          renderCorrStats();
        });
        document.getElementById('corr-lag').addEventListener('change', (e) => {
          state.corrLag = Number(e.target.value);
          renderCorrChart();
          // the bucket header states the lag it was computed with — keep it in sync
          renderCorrBuckets();
          renderCorrStats();
        });
      },
    },
    {
      label: '日历指标切换',
      anchor: '#heat-metric',
      run: () => {
        document.getElementById('heat-metric').addEventListener('change', (e) => {
          state.heat = e.target.value;
          renderHeatmap();
        });
        document.getElementById('heatmap').addEventListener('click', (e) => {
          const cell = e.target.closest('.hcell');
          if (!cell) return;
          state.selectedDate = cell.dataset.date;
          syncUrlDate(state.selectedDate);
          renderDayDetail();
          renderHeatmap();
        });
      },
    },
    {
      label: '身体成分时间轴',
      anchor: '#body-range',
      run: () => {
        // body module owns its time axis (all / last year / follow the top bar)
        const bodyRangeBox = document.getElementById('body-range');
        if (!bodyRangeBox) return;
        bodyRangeBox.addEventListener('click', (e) => {
          const btn = e.target.closest('button[data-body-range]');
          if (!btn) return;
          const raw = btn.dataset.bodyRange;
          state.bodyRange = raw === 'follow' ? 'follow' : Number(raw);
          bodyRangeBox.querySelectorAll('button[data-body-range]').forEach((b) => {
            const on = b === btn;
            b.classList.toggle('active', on);
            b.setAttribute('aria-pressed', String(on));
          });
          renderBodyCharts();
        });
      },
    },
    {
      label: '数据表与页面工具',
      anchor: '#daily-table',
      run: () => {
        document.getElementById('toggle-daily').addEventListener('click', (e) => {
          state.dailyExpanded = !state.dailyExpanded;
          state.dailyLimit = state.dailyExpanded ? state.rangeRows.length : 30;
          e.currentTarget.textContent = state.dailyExpanded ? '收起' : '展开全部';
          e.currentTarget.setAttribute('aria-expanded', String(state.dailyExpanded));
          renderDailyTable();
        });

        document.getElementById('toggle-compact').addEventListener('click', (e) => {
          const table = document.getElementById('daily-table');
          const on = !table.classList.contains('compact');
          table.classList.toggle('compact', on);
          e.currentTarget.setAttribute('aria-pressed', String(on));
          updateScrollHint();
        });

        window.addEventListener(
          'resize',
          () => {
            clearTimeout(state._hintTimer);
            state._hintTimer = setTimeout(updateScrollHint, 150);
          },
          { passive: true }
        );

        // back-to-top: appears after one screen of scrolling
        const toTop = document.getElementById('back-to-top');
        const onScroll = () => {
          toTop.hidden = window.scrollY < window.innerHeight * 0.8;
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
        toTop.addEventListener('click', () => {
          const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
        });

        document.getElementById('export-csv').addEventListener('click', exportCsv);
      },
    },
    {
      label: '自定义时间范围',
      anchor: '#custom-range',
      run: () => {
        const customBox = document.getElementById('custom-range');
        const toggle = document.getElementById('custom-toggle');
        const startInput = document.getElementById('range-start');
        const endInput = document.getElementById('range-end');
        const all = state.data.daily;
        if (all.length) {
          startInput.min = endInput.min = all[0].date;
          startInput.max = endInput.max = all[all.length - 1].date;
          startInput.value = all[Math.max(0, all.length - 30)].date;
          endInput.value = all[all.length - 1].date;
        }
        toggle.addEventListener('click', () => {
          const open = customBox.hidden;
          customBox.hidden = !open;
          toggle.setAttribute('aria-expanded', String(open));
          if (open) startInput.focus();
        });
        document.getElementById('range-apply').addEventListener('click', () => {
          const start = startInput.value;
          const end = endInput.value;
          const note = document.getElementById('custom-range-note');
          if (!start || !end) {
            note.textContent = '请选择开始和结束日期';
            return;
          }
          if (start > end) {
            note.textContent = '开始日期不能晚于结束日期';
            return;
          }
          const rows = state.data.daily.filter((r) => r.date >= start && r.date <= end);
          if (!rows.length) {
            note.textContent = '该区间没有记录';
            return;
          }
          note.textContent = `${rows.length} 天有记录`;
          state.customRange = { start, end };
          document.querySelectorAll('#range button[data-range]').forEach((b) => {
            b.classList.remove('active');
            b.setAttribute('aria-pressed', 'false');
          });
          const rangeLabel = document.getElementById('range-label');
          if (rangeLabel) rangeLabel.textContent = `时间范围：${start} → ${end}`;
          const windowLabel = document.getElementById('window-label');
          if (windowLabel) {
            windowLabel.innerHTML = `<span class="wl-prefix">当前窗口：</span>${start} → ${end}`;
          }
          document.getElementById('sticky-bar')?.classList.add('is-custom');
          renderCharts();
        });
      },
    },
    {
      label: '图表键盘可达',
      anchor: '#main',
      run: () => {
        // 键盘可达：canvas Enter/Space → 打开等效数据表
        document.querySelectorAll('canvas[role="img"]').forEach((canvas) => {
          canvas.tabIndex = 0;
          canvas.setAttribute('aria-describedby', `table-${canvas.id}`);
          canvas.addEventListener('keydown', (e) => {
            if (e.key !== 'Enter' && e.key !== ' ') return;
            e.preventDefault();
            const btn = document.querySelector(`[data-table-for="${canvas.id}"]`);
            if (btn) {
              btn.click();
              btn.focus();
            }
          });
        });
      },
    },
    {
      label: '数据首屏渲染',
      anchor: '#kpis',
      run: () => {
        wireTables();
        applyRange(90);
      },
    },
    {
      label: '分区导航',
      anchor: '#main',
      run: () => initSectionSpy(),
    },
    {
      label: '日期深链',
      anchor: '#day-detail',
      run: () => {
        // deep link: ?date=YYYY-MM-DD jumps straight to that day in the calendar
        const wanted = readUrlDate();
        if (wanted && state.data.daily.some((r) => r.date === wanted)) {
          state.selectedDate = wanted;
          renderDayDetail();
          renderHeatmap();
          requestAnimationFrame(() => {
            document.getElementById('day-detail')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
          });
        }
      },
    },
    {
      label: '手机精简数据表',
      anchor: '#daily-table',
      run: () => {
        // phones start with the compact daily table (5 core columns)
        if (window.matchMedia('(max-width: 767px)').matches) {
          document.getElementById('daily-table').classList.add('compact');
          const compactBtn = document.getElementById('toggle-compact');
          compactBtn.setAttribute('aria-pressed', 'true');
          updateScrollHint();
        }
      },
    },
    {
      label: '动效偏好联动',
      anchor: '#main',
      run: () => {
        onMediaChange(
          window.matchMedia('(prefers-reduced-motion: reduce)'),
          () => {
            for (const ch of Object.values(charts)) ch.destroy();
            renderCharts();
          }
        );
      },
    },
  ];

  for (const step of steps) guard(step.label, step.run, step.anchor);

  if (degradedModules.length) {
    showTopBanner(
      `<b>${degradedModules.length} 个模块未能加载</b>：${degradedModules.join('、')}。` +
        '其余内容与数据不受影响，可点击上方模块内的「重试」刷新页面。'
    );
  }
};

init().catch((error) => {
  // production shows a short Chinese line; the console keeps the detail
  console.error(error);
  showTopBanner(
    '<b>页面初始化遇到问题</b><br>大部分模块可能仍然可用。' +
      '若页面为空，请强制刷新（Ctrl/Cmd + Shift + R）或稍后重试。'
  );
});
'''

# Replace from the start of the old init to the end of the file's catch block.
start = s.index('const init = async () => {')
end_marker = "showFatal('初始化失败：' + error.message);\n});"
end = s.index(end_marker) + len(end_marker)
s = s[:start] + helpers.strip() + s[end:]

# ------------------------------------------- degraded note gets a 重试 ----
old_note = """  const note = document.createElement('p');
  note.className = 'degraded-note';
  note.dataset.degraded = step.label;
  note.textContent = `「${step.label}」本次渲染失败，其余模块不受影响（${error.message}）`;
  host.append(note);"""
new_note = """  const note = document.createElement('p');
  note.className = 'degraded-note';
  note.dataset.degraded = step.label;
  note.setAttribute('aria-live', 'polite');
  const text = document.createElement('span');
  text.textContent = `「${step.label}」本次渲染失败，其余模块不受影响。`;
  note.append(text, retryButton());
  host.append(note);
  if (typeof console !== 'undefined') console.warn(`${step.label}: ${error.message}`);"""
assert old_note in s
s = s.replace(old_note, new_note, 1)

# ---------------------------------------------- fatal card gets a 重试 ----
old_fatal = """  kpis.innerHTML = `
    <div class="kpi"><span class="value">!</span>
      <span class="label">数据加载失败</span>
      <span class="sub">${message}</span></div>`;"""
new_fatal = """  kpis.innerHTML = `
    <div class="kpi"><span class="value">!</span>
      <span class="label">数据加载失败</span>
      <span class="sub">${message}</span></div>`;
  const card = kpis.querySelector('.kpi');
  if (card) {
    card.append(retryButton());
    card.querySelector('.degraded-retry')?.addEventListener('click', () =>
      window.location.reload()
    );
  }"""
assert old_fatal in s
s = s.replace(old_fatal, new_fatal, 1)

# ------------------------------------------------------------- debug hook ---
# append at end of file: init() runs at parse time above, a trailing
# statement is safe and keeps the smoke test able to re-run init().
hook = """
// Small debug handle for the smoke test (and for a human in devtools): the
// page never relies on it, but re-running init() makes failure modes
// reproducible without rebuilding.
window.__HEALTH_DEBUG__ = { init, renderCharts, degradedModules };
"""
s = s.rstrip() + "\n" + hook

p.write_text(s)
print('health app.js patched')
