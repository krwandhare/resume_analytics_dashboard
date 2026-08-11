import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def generate_analytics(job_data: pd.DataFrame, events_df: pd.DataFrame = None, apps_df: pd.DataFrame = None) -> None:
    """Generate visual analytics in a clean 2x2 grid layout."""
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

    # Row 1: Active Landscape (Pie Chart) & Match Score Distribution (Histogram)
    r1_col1, r1_col2 = st.columns(2)

    with r1_col1:
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
                height=320
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=0, r=0),
                font=dict(family="Inter, sans-serif", color="#F8FAFC")
            )
            st.plotly_chart(fig_pie, width="stretch")
        else:
            st.info("Status distribution data not available.")

    with r1_col2:
        st.markdown("### Match Score Distribution")
        st.caption("Are you targeting the right roles based on your resume?")
        
        if 'match_score' in job_data.columns and not job_data['match_score'].dropna().empty:
            score_df = job_data.dropna(subset=['match_score']).copy()
            
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
                height=320,
                font=dict(family="Inter, sans-serif", color="#F8FAFC")
            )
            st.plotly_chart(fig_hist, width="stretch")
        else:
            st.info("Match score data not available for visualization.")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Row 2: Top Companies Targeted (Bar Chart) & Application Velocity (Area Chart)
    r2_col1, r2_col2 = st.columns(2)

    with r2_col1:
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
                    height=320
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

    with r2_col2:
        st.markdown("### Application Velocity & Momentum")
        st.caption("Track your application submission volume and response pace over time.")

        time_series_records = []
        if 'first_seen_at' in job_data.columns:
            for d in job_data['first_seen_at'].dropna():
                dt = pd.to_datetime(d, errors='coerce')
                if pd.notnull(dt):
                    time_series_records.append({'date': dt, 'source': 'Live Tracker'})

        if apps_df is not None and not apps_df.empty and 'applied_at' in apps_df.columns:
            for d in apps_df['applied_at'].dropna():
                dt = pd.to_datetime(d, errors='coerce')
                if pd.notnull(dt):
                    time_series_records.append({'date': dt, 'source': 'Historical'})

        if time_series_records:
            ts_df = pd.DataFrame(time_series_records)
            ts_df['date'] = ts_df['date'].dt.tz_localize(None)
            ts_df['week'] = ts_df['date'].dt.to_period('W').dt.start_time

            weekly_counts = ts_df.groupby('week').size().reset_index(name='Applications')
            weekly_counts = weekly_counts.sort_values('week')

            fig_velocity = px.area(
                weekly_counts,
                x='week',
                y='Applications',
                markers=True,
                color_discrete_sequence=['#6366F1'],
                labels={'week': 'Week Starting', 'Applications': 'Applications Submitted'}
            )
            fig_velocity.update_traces(
                fillcolor='rgba(99, 102, 241, 0.25)',
                line=dict(width=3, color='#818CF8')
            )
            fig_velocity.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
                margin=dict(t=20, b=20, l=0, r=0),
                height=320,
                font=dict(family="Inter, sans-serif", color="#F8FAFC")
            )
            st.plotly_chart(fig_velocity, width="stretch")
        else:
            st.info("No dated application records available for momentum analytics.")


