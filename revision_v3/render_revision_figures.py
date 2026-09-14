"""Render revision figures with the manuscript's Tinos typography."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.font_manager import fontManager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'manuscript' / 'figs' / 'rendered'
PLOT = ROOT / 'revision_v3' / 'analyses'
fontManager.addfont('/usr/share/fonts/truetype/croscore/Tinos-Regular.ttf')
fontManager.addfont('/usr/share/fonts/truetype/croscore/Tinos-Bold.ttf')
plt.rcParams.update({'font.family':'Tinos','font.size':8.5,'axes.titlesize':9.5,'axes.labelsize':8.5,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':8.5,'pdf.fonttype':42,'ps.fonttype':42})
COL = {'openst':'#0072B2','realgt':'#E69F00','realgt3':'#009E73'}
PRETTY = {'openst':'openST','realgt':'Xenium','realgt3':'CosMx'}

def panel_title(ax, label, title):
    ax.text(-0.12, 1.16, label, transform=ax.transAxes, ha='left', va='top', fontweight='bold', fontsize=14)
    ax.text(-0.01, 1.13, title, transform=ax.transAxes, ha='left', va='top', fontsize=11)

def clean(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(width=.55, length=3)
    ax.grid(False)

def render_f13():
    summ = pd.read_csv(PLOT/'reporting'/'neighbor_max_rule_library_summary.csv')
    denom = pd.read_csv(PLOT/'reporting'/'neighbor_denominator_reconciliation.csv')
    pert = pd.read_csv(PLOT/'perturbation'/'perturbation_summary.csv')
    fig, ax = plt.subplots(2,2, figsize=(8.6,6.2), dpi=300)
    a,b,c,d = ax.flat
    order=['CosMx CRC','CosMx HCC','CosMx NSCLC','CosMx PDAC']; x=range(len(order))
    h=summ.set_index('library').loc[order]
    a.scatter(x,h['historical_cosine'],s=27,c='#4F9F7A',label='historical designated',zorder=3)
    a.scatter(x,h['selected_cosine_max_rule'],s=27,c='#D6A12A',label='all eligible maximum',zorder=3)
    a.axhline(.8,color='#D17A00',ls='--',lw=.8); a.set_ylim(.47,.93); a.set_ylabel('malignant-neighbor cosine'); a.set_xticks(list(x),['CosMx CRC','CosMx HCC','CosMx NSCLC','CosMx PDAC'],rotation=18,ha='right'); panel_title(a,'A','Designated versus all-eligible rule'); clean(a)
    a.legend(loc='lower center',bbox_to_anchor=(.5,1.24),ncol=2,frameon=False,handletextpad=.4,columnspacing=.8)
    bd=denom.set_index('library').loc[order]
    xx=list(range(len(order))); a0=bd['eligible_rows']; a1=bd['excluded_rows'];
    b.bar(xx,a0,color='#4F9F7A',label='eligible'); b.bar(xx,a1,bottom=a0,color='#C06A24',label='excluded'); b.set_ylabel('neighbor rows'); b.set_xticks(xx,['CosMx CRC','CosMx HCC','CosMx NSCLC','CosMx PDAC'],rotation=18,ha='right'); b.set_ylim(0,18); panel_title(b,'B','Denominator reconciliation'); clean(b)
    b.legend(handles=[Line2D([0],[0],marker='s',color='#B8C4CF',lw=0,markersize=6,label='stored rows'),Line2D([0],[0],marker='s',color='#C06A24',lw=0,markersize=6,label='excluded'),Line2D([0],[0],marker='s',color='#4F9F7A',lw=0,markersize=6,label='eligible')],loc='lower center',bbox_to_anchor=(.5,1.24),ncol=3,frameon=False,handletextpad=.3,columnspacing=.6)
    for sub in ['openst','realgt','realgt3']:
        q=pert[pert.substrate==sub].sort_values('fraction'); c.errorbar(q.fraction*100,q.historical_cosine_mean,yerr=q.historical_cosine_sd.fillna(0),marker='o',lw=1.4,ms=4,color=COL[sub],label=PRETTY[sub])
    c.axhline(.8,color='#D17A00',ls='--',lw=.8); c.set_ylim(.45,1.0); c.set_xlabel('reference genes retained (%)'); c.set_ylabel('cosine'); c.set_xticks([50,75,100]); panel_title(c,'C','Reference perturbation preserves calls'); clean(c)
    for sub in ['openst','realgt','realgt3']:
        q=pert[pert.substrate==sub].sort_values('fraction'); d.errorbar(q.fraction*100,q.malignant_rmse_mean,yerr=q.malignant_rmse_sd.fillna(0),marker='o',lw=1.4,ms=4,color=COL[sub])
    d.set_ylim(.07,.19); d.set_xlabel('reference genes retained (%)'); d.set_ylabel('malignant RMSE'); d.set_xticks([50,75,100]); panel_title(d,'D','Accuracy cost under gene loss'); clean(d)
    fig.legend(handles=[Line2D([0],[0],marker='o',color=COL[s],lw=1.4,markersize=4,label=PRETTY[s]) for s in ['openst','realgt','realgt3']],loc='lower center',bbox_to_anchor=(.75,.015),ncol=3,frameon=False,handletextpad=.35,columnspacing=.8)
    fig.subplots_adjust(left=.105,right=.985,top=.78,bottom=.22,wspace=.33,hspace=.62)
    fig.savefig(OUT/'F13_revision_audit.pdf',pad_inches=.03); fig.savefig(OUT/'F13_v3_rule_and_perturbation.pdf',bbox_inches='tight',pad_inches=.02); plt.close(fig)

if __name__=='__main__': render_f13()
