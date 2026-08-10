import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def generate_analytics(job_data: pd.DataFrame, events_df: pd.DataFrame = None, apps_df: pd.DataFrame = None) -> None:
    """Generate visual analytics safely from job data."""
    if not isinstance(job_data, pd.DataFrame) or job_data.empty:
        st.warning("No job data available for visualization.")
        return

    with st.expander("📖 How to read this data", expanded=False):
        st.markdown("""
        **Spotting Bottlenecks in Your Job Search:**
        - **Funnel Drop-offs:** If your applications aren't converting to interviews, your resume may not be passing the ATS. Check your match scores in the Details tab.
        - **Timeline Slowdowns:** If your application volume drops over time, you might need to broaden your search criteria or set a daily goal.
        """)

    # Semantic Color Palette
    STATUS_COLORS = {
        'Hired': '#10B981',
        'Offer Received': '#34D399',
        'Offer': '#34D399',
        'Interviewing': '#F59E0B',
        'Reviewing': '#60A5FA',
        'Applied': '#3B82F6',
        'Pending': '#93C5FD',
        'Rejected': '#EF4444',
        'Unknown': '#6B7280'
    }

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### The Big Picture: Your Application Funnel")
        st.caption("How your historical applications have progressed through the hiring pipeline.")
        
        # True Accumulating Funnel Logic
        total_apps = 0
        total_interviews = 0
        total_offers = 0
        total_hired = 0
        
        if apps_df is not None and not apps_df.empty:
            total_apps = len(apps_df)
            
        if events_df is not None and not events_df.empty and 'event_type' in events_df.columns:
            ev_norm = events_df.copy()
            ev_norm['event_type'] = ev_norm['event_type'].astype(str).str.lower()
            
            # Any app that reached interview, offer, or hired
            int_apps = ev_norm[ev_norm['event_type'].isin(['interviewing', 'offer', 'offer received', 'hired'])]
            total_interviews = int_apps['application_id'].nunique() if 'application_id' in int_apps.columns else 0
            
            # Any app that reached offer or hired
            off_apps = ev_norm[ev_norm['event_type'].isin(['offer', 'offer received', 'hired'])]
            total_offers = off_apps['application_id'].nunique() if 'application_id' in off_apps.columns else 0
            
            # Any app that was hired
            hire_apps = ev_norm[ev_norm['event_type'] == 'hired']
            total_hired = hire_apps['application_id'].nunique() if 'application_id' in hire_apps.columns else 0

        # Graphical Chevron Pipeline
        st.write("") # Spacing
        
        if total_apps > 0:
            pipeline_html = f"""
            <style>
            .chevron-pipeline { display: flex; width: 100%; margin: 10px 0; }
            .chevron-step {
                flex-grow: 1; text-align: center; padding: 12px 0; color: white;
                font-weight: bold; position: relative; margin-right: 4px;
                clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%, 15px 50%);
            }
            .chevron-step:first-child { clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%); }
            .chevron-step:last-child { clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%, 15px 50%); margin-right: 0; }
            .step-applied { background-color: #3B82F6; }
            .step-interview { background-color: #F59E0B; }
            .step-offer { background-color: #34D399; }
            .step-hired { background-color: #10B981; }
            .chevron-count { font-size: 1.4em; display: block; line-height: 1.2; }
            .chevron-label { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; }

            @media (max-width: 600px) {
                .chevron-pipeline { flex-wrap: wrap; gap: 6px; }
                .chevron-step {
                    clip-path: none !important;
                    border-radius: 8px !important;
                    margin-right: 0 !important;
                    flex-basis: 48%;
                    padding: 8px 4px !important;
                }
                .chevron-count { font-size: 1.2em !important; }
                .chevron-label { font-size: 0.7em !important; }
            }
            </style>
            <div class="chevron-pipeline">
                <div class="chevron-step step-applied"><span class="chevron-count">{total_apps}</span><span class="chevron-label">Applied</span></div>
                <div class="chevron-step step-interview"><span class="chevron-count">{total_interviews}</span><span class="chevron-label">Interviewing</span></div>
                <div class="chevron-step step-offer"><span class="chevron-count">{total_offers}</span><span class="chevron-label">Offers</span></div>
                <div class="chevron-step step-hired"><span class="chevron-count">{total_hired}</span><span class="chevron-label">Hired</span></div>
            </div>
            """
            st.markdown(pipeline_html, unsafe_allow_html=True)
        else:
            st.info("No pipeline progression data available yet.")

    with col2:
        st.markdown("### Current Active Landscape")
        st.caption("The current status of jobs in your live tracker.")
        
        if 'status' in job_data.columns and not job_data['status'].dropna().empty:
            status_df = job_data.copy()
            status_df['status'] = status_df['status'].astype(str).str.title()
            status_counts = status_df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig_pie = px.pie(
                status_counts, 
                names='Status',
                values='Count',
                color='Status',
                color_discrete_map=STATUS_COLORS,
                hole=0.4,
                height=350
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=0, r=0),
                font=dict(family="Inter, sans-serif", color="#F8FAFC")
            )
            st.plotly_chart(fig_pie, width="stretch")
            
            with st.expander("💡 Insights: What does this mean?"):
                st.markdown("""
                This chart shows the distribution of your **active** job search.
                - **Lots of Blue (Applied/Pending)?** You're sending out resumes, but they aren't converting. Consider tailoring your resume more heavily to the job description.
                - **Lots of Orange/Green (Interviewing/Offers)?** Your resume is working perfectly! Focus your time on interview preparation.
                - **Stagnant Pipeline?** If applications sit in "Applied" for more than 2 weeks, they are likely ghosted. Focus on new opportunities.
                """)
        else:
            st.info("Status distribution data not available.")

    st.markdown("---")
    
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Match Score Distribution")
        st.caption("Are you targeting the right roles based on your resume?")
        
        if 'match_score' in job_data.columns and not job_data['match_score'].dropna().empty:
            score_df = job_data.dropna(subset=['match_score']).copy()
            
            # Color code based on score quality
            def score_color(score):
                if score >= 80: return 'High Match (>80%)'
                if score >= 50: return 'Medium Match (50-80%)'
                return 'Low Match (<50%)'
                
            score_df['Match Quality'] = score_df['match_score'].apply(score_color)
            
            color_map = {
                'High Match (>80%)': '#10B981',
                'Medium Match (50-80%)': '#F59E0B',
                'Low Match (<50%)': '#EF4444'
            }
            
            existing_categories = score_df['Match Quality'].unique()
            ordered_cats = [c for c in ['High Match (>80%)', 'Medium Match (50-80%)', 'Low Match (<50%)'] if c in existing_categories]
            filtered_map = {k: color_map[k] for k in ordered_cats}
            
            fig_hist = go.Figure()
            for cat in ordered_cats:
                cat_df = score_df[score_df['Match Quality'] == cat]
                fig_hist.add_trace(go.Histogram(
                    x=cat_df['match_score'],
                    name=cat,
                    marker_color=color_map[cat],
                    nbinsx=15,
                    hovertemplate="Match Score: %{x}%<br>Count: %{y}<extra></extra>"
                ))
                
            fig_hist.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                barmode='stack',
                bargap=0.1, 
                margin=dict(t=20, b=20, l=0, r=0), 
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                xaxis_title="Match Score (%)",
                yaxis_title="count",
                height=350,
                font=dict(family="Inter, sans-serif", color="#F8FAFC")
            )
            st.plotly_chart(fig_hist, width="stretch")
        else:
            st.info("Match score data not available for visualization.")
            
    with col4:
        st.markdown("### Top Companies Targeted")
        st.caption("Companies you have applied to the most.")
        if 'company' in job_data.columns and not job_data['company'].dropna().empty:
            company_counts = job_data['company'].value_counts().head(10).reset_index()
            company_counts.columns = ['Company', 'Job Count']
            
            if len(company_counts) >= 2:
                fig_bar = px.bar(
                    company_counts, 
                    x='Job Count',
                    y='Company',
                    orientation='h',
                    color_discrete_sequence=['#3B82F6'],
                    height=300
                )
                fig_bar.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis={'categoryorder': 'total ascending'}, 
                    margin=dict(t=20, b=20, l=0, r=0),
                    font=dict(family="Inter, sans-serif", color="#F8FAFC")
                )
                st.plotly_chart(fig_bar, width="stretch")
            else:
                st.info("Not enough company data to show trends.")
        else:
            st.info("Company data not available.")
