import streamlit as st
import time
from datetime import datetime
from src.config import DB_NAME, DB_PASSWORD, DB_USER
from src.db import PostgreStorage

# Configure Streamlit page
st.set_page_config(
    page_title="Neuromedia News Feed",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_database():
    """Initialize database connection"""
    try:
        return PostgreStorage(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def format_tags(tags):
    """Format tags as colored pills"""
    if not tags:
        return ""
    
    tag_html = ""
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3", "#54A0FF"]
    
    for i, tag in enumerate(tags):
        color = colors[i % len(colors)]
        tag_html += f"""
        <span style="
            background-color: {color}; 
            color: white; 
            padding: 4px 8px; 
            border-radius: 15px; 
            font-size: 12px; 
            margin: 2px;
            display: inline-block;
        ">{tag}</span>
        """
    return tag_html

def display_news_item(news_item):
    """Display a single news item"""
    news_id, text, tags = news_item['id'], news_item['text'], news_item['tags']
    
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd; 
            border-radius: 10px; 
            padding: 15px; 
            margin: 10px 0; 
            background-color: #f9f9f9;
        ">
            <div style="color: #666; font-size: 12px; margin-bottom: 8px;">
                News ID: {news_id}
            </div>
            <div style="font-size: 16px; line-height: 1.5; margin-bottom: 10px;">
                {text}
            </div>
            <div>
                {format_tags(tags)}
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("📰 Neuromedia News Feed")
    st.markdown("Real-time news feed with AI-generated tags")
    
    # Sidebar controls
    st.sidebar.header("Feed Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh every 30 seconds", value=True)
    refresh_button = st.sidebar.button("🔄 Refresh Now")
    
    # Tag filter
    st.sidebar.header("Filter by Tags")
    
    # Initialize database
    db = init_database()
    if db is None:
        return
    
    # Get all records
    try:
        all_records = db.get_all()
        
        if not all_records:
            st.info("No news items found. The feed will update as new news is processed.")
            if auto_refresh:
                # Create a placeholder for auto-refresh status
                placeholder = st.empty()
                for seconds in range(30, 0, -1):
                    placeholder.text(f"⏱️ Refreshing in {seconds} seconds...")
                    time.sleep(1)
                placeholder.empty()
                st.rerun()
            return
        
        # Extract all unique tags for filtering
        all_tags = set()
        for record in all_records:
            if record['tags']:
                all_tags.update(record['tags'])
        
        selected_tags = st.sidebar.multiselect(
            "Select tags to filter:",
            options=sorted(all_tags),
            default=[]
        )
        
        # Filter records by selected tags
        if selected_tags:
            filtered_records = []
            for record in all_records:
                if record['tags'] and any(tag in record['tags'] for tag in selected_tags):
                    filtered_records.append(record)
        else:
            filtered_records = all_records
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total News", len(all_records))
        with col2:
            st.metric("Filtered News", len(filtered_records))
        with col3:
            st.metric("Unique Tags", len(all_tags))
        with col4:
            current_time = datetime.now().strftime("%H:%M:%S")
            st.metric("Last Updated", current_time)
        
        st.markdown("---")
        
        # Display news items
        if filtered_records:
            st.subheader(f"📄 News Feed ({len(filtered_records)} items)")
            
            for news_item in filtered_records:
                display_news_item(news_item)
        else:
            st.info("No news items match the selected tag filters.")
        
        # Auto-refresh functionality
        if auto_refresh or refresh_button:
            # Create a placeholder for countdown
            placeholder = st.empty()
            if not refresh_button:  # Only show countdown for auto-refresh
                for seconds in range(30, 0, -1):
                    placeholder.text(f"⏱️ Auto-refreshing in {seconds} seconds... (Uncheck 'Auto-refresh' to disable)")
                    time.sleep(1)
            placeholder.empty()
            st.rerun()
    
    except Exception as e:
        st.error(f"Error retrieving news: {e}")
    
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 