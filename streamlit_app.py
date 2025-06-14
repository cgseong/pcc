import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="닥치고 코딩",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# 로그인 함수
def login():
    st.sidebar.markdown("### 🔐 관리자 로그인")
    username = st.sidebar.text_input("아이디")
    password = st.sidebar.text_input("비밀번호", type="password")
    
    if st.sidebar.button("로그인"):
        if username == "admin" and password == "admin3738!":
            st.session_state.authenticated = True
            st.session_state.is_admin = True
            st.sidebar.success("관리자로 로그인되었습니다.")
            st.rerun()
        else:
            st.sidebar.error("아이디 또는 비밀번호가 올바르지 않습니다.")

# 로그아웃 함수
def logout():
    if st.sidebar.button("로그아웃"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()

# 스타일 설정
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
        margin: 0.5rem 0;
    }
    .filter-section {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 캐시된 데이터 로딩 함수
@st.cache_data
def load_data():
    """CSV 파일을 로드하고 전처리"""
    try:
        df = pd.read_csv('부산대학교_PCC_응시결과.csv')
        
        # 데이터 전처리
        df['합격여부_binary'] = df['합격여부'].map({'합격': 1, '불합격': 0})
        df['학년'] = df['학년'].astype(str)
        df['회차'] = df['회차'].astype(int)
        
        # 등급이 비어있는 경우 처리
        df['등급(Lv.)'] = df['등급(Lv.)'].fillna('없음')
        
        return df
    except Exception as e:
        st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")
        return None

# 메인 애플리케이션
def main():
    st.markdown('<h1 class="main-header">🏆 부산대학교 PCC 응시현황</h1>', unsafe_allow_html=True)
    
    # 데이터 로딩
    df = load_data()
    if df is None:
        return
    
    # 사이드바 - 데이터 필터링 메뉴
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.header("🔍 데이터 필터링")
    
    # 학과 선택 (다중선택)
    departments = st.sidebar.multiselect(
        "학과 선택",
        options=sorted(df['학과'].unique()),
        default=sorted(df['학과'].unique()),
        help="분석할 학과를 선택하세요"
    )
    
    # 학년 선택
    grades = st.sidebar.multiselect(
        "학년 선택",
        options=sorted(df['학년'].unique()),
        default=sorted(df['학년'].unique()),
        help="분석할 학년을 선택하세요"
    )
    
    # 합격 여부 선택
    pass_status = st.sidebar.multiselect(
        "합격 여부 선택",
        options=['합격', '불합격'],
        default=['합격', '불합격'],
        help="분석할 합격 여부를 선택하세요"
    )
    
    # 등급 선택
    levels = st.sidebar.multiselect(
        "등급 선택",
        options=sorted(df['등급(Lv.)'].unique()),
        default=sorted(df['등급(Lv.)'].unique()),
        help="분석할 등급을 선택하세요"
    )
    
    # 시험과목 선택
    subjects = st.sidebar.multiselect(
        "시험과목 선택",
        options=sorted(df['시험과목'].unique()),
        default=sorted(df['시험과목'].unique()),
        help="분석할 시험과목을 선택하세요"
    )
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # 관리자 로그인 섹션
    login()
    if st.session_state.is_admin:
        logout()
    
    # 데이터 필터링 적용
    filtered_df = df[
        (df['학과'].isin(departments)) &
        (df['학년'].isin(grades)) &
        (df['합격여부'].isin(pass_status)) &
        (df['등급(Lv.)'].isin(levels)) &
        (df['시험과목'].isin(subjects))
    ]
    
    if filtered_df.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        return
    
    # 탭 생성
    if st.session_state.is_admin:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 전체 정보", 
            "📈 정보컴퓨터공학부 회차별 현황", 
            "🎓 정보컴퓨터공학부 학년별 통계", 
            "👨‍🎓 학생별 성과 분석",
            "📋 상세 데이터",
            "📈 성장 추이 분석"
        ])
    else:
        tab1, tab2, tab3 = st.tabs([
            "📊 전체 정보", 
            "📈 정보컴퓨터공학부 회차별 현황", 
            "🎓 정보컴퓨터공학부 학년별 통계"
        ])
    
    # 탭 1: 전체 정보
    with tab1:
        st.header("📊 전체 응시 정보")
        
        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)
        
        total_applicants = len(filtered_df)
        total_passed = len(filtered_df[filtered_df['합격여부'] == '합격'])
        total_pass_rate = (total_passed / total_applicants * 100) if total_applicants > 0 else 0
        avg_score = filtered_df['총점'].mean()
        
        with col1:
            st.metric(
                label="전체 응시자수",
                value=f"{total_applicants:,}명"
            )
        
        with col2:
            st.metric(
                label="전체 합격률",
                value=f"{total_pass_rate:.1f}%"
            )
        
        with col3:
            st.metric(
                label="전체 평균점수",
                value=f"{avg_score:.1f}점"
            )
        
        with col4:
            st.metric(
                label="합격자수",
                value=f"{total_passed:,}명"
            )
        
        st.markdown("---")
        
        # 상세 통계
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 학과별 통계")
            dept_stats = filtered_df.groupby('학과').agg({
                '이름': 'count',
                '합격여부_binary': ['sum', 'mean'],
                '총점': 'mean'
            }).round(2)
            dept_stats.columns = ['응시자수', '합격자수', '합격률', '평균점수']
            dept_stats['합격률'] = (dept_stats['합격률'] * 100).round(1).astype(str) + '%'
            st.dataframe(dept_stats, use_container_width=True)
        
        with col2:
            st.subheader("📊 시험과목별 통계")
            subject_stats = filtered_df.groupby('시험과목').agg({
                '이름': 'count',
                '합격여부_binary': ['sum', 'mean'],
                '총점': 'mean'
            }).round(2)
            subject_stats.columns = ['응시자수', '합격자수', '합격률', '평균점수']
            subject_stats['합격률'] = (subject_stats['합격률'] * 100).round(1).astype(str) + '%'
            st.dataframe(subject_stats, use_container_width=True)
    
    # 탭 2: 정보컴퓨터공학부 회차별 현황
    with tab2:
        st.header("📈 정보컴퓨터공학부 회차별 응시자 현황")
        
        # 정보컴퓨터공학부 데이터만 필터링
        cse_df = filtered_df[filtered_df['학과'] == '정보컴퓨터공학부']
        
        if cse_df.empty:
            st.warning("정보컴퓨터공학부 데이터가 없습니다.")
        else:
            # 회차별 통계 계산
            round_stats = cse_df.groupby('회차').agg({
                '이름': 'count',
                '합격여부_binary': 'sum',
                '총점': 'mean'
            }).reset_index()
            round_stats.columns = ['회차', '총_응시자수', '합격자수', '평균점수']
            round_stats['불합격자수'] = round_stats['총_응시자수'] - round_stats['합격자수']
            round_stats['합격률'] = (round_stats['합격자수'] / round_stats['총_응시자수'] * 100).round(1)
            
            # 그래프 생성
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('응시자수 추이', '합격률 추이', '합격/불합격 현황', '평균점수 추이'),
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # 응시자수 추이
            fig.add_trace(
                go.Scatter(x=round_stats['회차'], y=round_stats['총_응시자수'],
                          mode='lines+markers+text', name='응시자수',
                          line=dict(color='blue', width=3),
                          text=round_stats['총_응시자수'],
                          textposition='top center'),
                row=1, col=1
            )
            
            # 합격률 추이
            fig.add_trace(
                go.Scatter(x=round_stats['회차'], y=round_stats['합격률'],
                          mode='lines+markers+text', name='합격률(%)',
                          line=dict(color='green', width=3),
                          text=[f"{x:.1f}%" for x in round_stats['합격률']],
                          textposition='top center'),
                row=1, col=2
            )
            
            # 합격/불합격 현황
            fig.add_trace(
                go.Bar(x=round_stats['회차'], y=round_stats['합격자수'],
                      name='합격자수', marker_color='lightgreen',
                      text=round_stats['합격자수'],
                      textposition='inside'),
                row=2, col=1
            )
            fig.add_trace(
                go.Bar(x=round_stats['회차'], y=round_stats['불합격자수'],
                      name='불합격자수', marker_color='lightcoral',
                      text=round_stats['불합격자수'],
                      textposition='inside'),
                row=2, col=1
            )
            
            # 평균점수 추이
            fig.add_trace(
                go.Scatter(x=round_stats['회차'], y=round_stats['평균점수'],
                          mode='lines+markers+text', name='평균점수',
                          line=dict(color='orange', width=3),
                          text=[f"{x:.1f}" for x in round_stats['평균점수']],
                          textposition='top center'),
                row=2, col=2
            )
            
            fig.update_layout(
                height=600, 
                showlegend=True, 
                title_text="정보컴퓨터공학부 회차별 종합 현황",
                xaxis=dict(dtick=1),  # x축을 정수 단위로만 표시
                xaxis2=dict(dtick=1), # 두 번째 서브플롯의 x축
                xaxis3=dict(dtick=1), # 세 번째 서브플롯의 x축  
                xaxis4=dict(dtick=1)  # 네 번째 서브플롯의 x축
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 상세 통계 테이블
            st.subheader("📋 회차별 상세 통계")
            st.dataframe(round_stats, use_container_width=True)
    
    # 탭 3: 정보컴퓨터공학부 학년별 통계
    with tab3:
        st.header("🎓 정보컴퓨터공학부 학년별 통계")
        
        cse_df = filtered_df[filtered_df['학과'] == '정보컴퓨터공학부']
        
        if cse_df.empty:
            st.warning("정보컴퓨터공학부 데이터가 없습니다.")
        else:
            # 학년별 통계
            grade_stats = cse_df.groupby('학년').agg({
                '이름': 'count',
                '합격여부_binary': ['sum', 'mean'],
                '총점': ['mean', 'std']
            }).round(2)
            grade_stats.columns = ['응시자수', '합격자수', '합격률', '평균점수', '점수표준편차']
            grade_stats['합격률_pct'] = (grade_stats['합격률'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 학년별 응시자수 및 합격률
                fig1 = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig1.add_trace(
                    go.Bar(x=grade_stats.index, y=grade_stats['응시자수'],
                          name='응시자수', marker_color='lightblue',
                          text=grade_stats['응시자수'],
                          textposition='inside'),
                    secondary_y=False,
                )
                
                fig1.add_trace(
                    go.Scatter(x=grade_stats.index, y=grade_stats['합격률_pct'],
                              mode='lines+markers+text', name='합격률(%)',
                              line=dict(color='red', width=3),
                              text=[f"{x:.1f}%" for x in grade_stats['합격률_pct']],
                              textposition='top center'),
                    secondary_y=True,
                )
                
                fig1.update_xaxes(title_text="학년")
                fig1.update_yaxes(title_text="응시자수", secondary_y=False)
                fig1.update_yaxes(title_text="합격률(%)", secondary_y=True)
                fig1.update_layout(
                    title_text="학년별 응시자수 및 합격률",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # 학년별 평균점수
                fig2 = px.bar(x=grade_stats.index, y=grade_stats['평균점수'],
                             title="학년별 평균점수",
                             labels={'x': '학년', 'y': '평균점수'})
                fig2.update_traces(
                    marker_color='lightgreen',
                    text=grade_stats['평균점수'].round(1),
                    textposition='inside'
                )
                fig2.update_layout(
                    showlegend=False,
                    yaxis_title="평균점수"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # 상세 통계 테이블
            st.subheader("📋 학년별 상세 통계")
            display_stats = grade_stats.copy()
            display_stats['합격률'] = display_stats['합격률_pct'].astype(str) + '%'
            display_stats = display_stats.drop('합격률_pct', axis=1)
            st.dataframe(display_stats, use_container_width=True)
    
    # 관리자 전용 탭들
    if st.session_state.is_admin:
        # 탭 4: 학생별 성과 분석
        with tab4:
            st.header("👨‍🎓 학생별 성과 분석")
            
            # 3회 이상 응시자 찾기
            student_attempts = filtered_df.groupby(['이름', '이메일', '학번']).size().reset_index(name='응시횟수')
            frequent_test_takers = student_attempts[student_attempts['응시횟수'] >= 3]
            
            if frequent_test_takers.empty:
                st.info("3회 이상 응시한 학생이 없습니다.")
            else:
                st.subheader(f"📋 3회 이상 응시자 목록 ({len(frequent_test_takers)}명)")
                
                # 3회 이상 응시자의 상세 정보
                detailed_info = []
                for _, row in frequent_test_takers.iterrows():
                    student_data = filtered_df[
                        (filtered_df['이름'] == row['이름']) & 
                        (filtered_df['이메일'] == row['이메일']) &
                        (filtered_df['학번'] == row['학번'])
                    ].sort_values('회차')
                    
                    passes = len(student_data[student_data['합격여부'] == '합격'])
                    avg_score = student_data['총점'].mean()
                    max_score = student_data['총점'].max()
                    
                    detailed_info.append({
                        '이름': row['이름'],
                        '이메일': row['이메일'],
                        '학번': row['학번'],
                        '학과': student_data.iloc[0]['학과'],
                        '학년': student_data.iloc[0]['학년'],
                        '응시횟수': row['응시횟수'],
                        '합격횟수': passes,
                        '평균점수': round(avg_score, 1),
                        '최고점수': max_score
                    })
                
                detailed_df = pd.DataFrame(detailed_info)
                st.dataframe(detailed_df, use_container_width=True)
                
                # 점수 추이 분석
                st.subheader("📈 점수 추이 분석")
                
                # 학생 선택
                selected_student = st.selectbox(
                    "분석할 학생 선택",
                    options=[(f"{row['이름']} ({row['학번']}) - {row['이메일']}") for _, row in frequent_test_takers.iterrows()],
                    help="점수 추이를 확인할 학생을 선택하세요"
                )
                
                if selected_student:
                    # 선택된 학생의 정보 파싱
                    parts = selected_student.split(' - ')
                    email = parts[1]
                    name_and_id = parts[0]
                    student_name = name_and_id.split(' (')[0]
                    student_id = name_and_id.split('(')[1].split(')')[0]
                    
                    student_history = filtered_df[
                        (filtered_df['이름'] == student_name) & 
                        (filtered_df['이메일'] == email) &
                        (filtered_df['학번'] == student_id)
                    ].sort_values('회차')
                    
                    # 점수 추이 그래프
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=student_history['회차'],
                        y=student_history['총점'],
                        mode='lines+markers',
                        name='점수',
                        line=dict(color='blue', width=3),
                        marker=dict(size=10)
                    ))
                    
                    # 합격선 표시 (일반적으로 400점 이상을 합격으로 가정)
                    fig.add_hline(y=400, line_dash="dash", line_color="red", 
                                 annotation_text="합격선 (추정)")
                    
                    fig.update_layout(
                        title=f"{student_name}({student_id}) 점수 추이",
                        xaxis_title="회차",
                        yaxis_title="점수",
                        height=400,
                        xaxis=dict(dtick=1)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 상세 데이터
                    st.subheader("📋 회차별 상세 데이터")
                    display_history = student_history[['회차', '시험과목', '총점', '합격여부', '등급(Lv.)']].copy()
                    st.dataframe(display_history, use_container_width=True)
        
        # 탭 5: 상세 데이터
        with tab5:
            st.header("📋 전체 상세 데이터")
            
            # 데이터 요약
            st.subheader("📊 필터링된 데이터 요약")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 레코드 수", len(filtered_df))
            with col2:
                st.metric("고유 학생 수", filtered_df.groupby(['이름', '학번']).ngroups)
            with col3:
                st.metric("회차 범위", f"{filtered_df['회차'].min()} - {filtered_df['회차'].max()}")
            
            # 검색 기능
            st.subheader("🔍 데이터 검색")
            search_term = st.text_input("학생 이름 또는 학번으로 검색", placeholder="예: 김철수 또는 202155619")
            
            display_df = filtered_df.copy()
            if search_term:
                display_df = display_df[
                    (display_df['이름'].str.contains(search_term, case=False, na=False)) |
                    (display_df['학번'].astype(str).str.contains(search_term, case=False, na=False))
                ]
            
            # 정렬 옵션
            sort_col = st.selectbox(
                "정렬 기준",
                options=['회차', '총점', '이름', '학과', '학년'],
                index=0
            )
            sort_order = st.radio("정렬 순서", ["오름차순", "내림차순"], horizontal=True)
            
            ascending = True if sort_order == "오름차순" else False
            display_df = display_df.sort_values(sort_col, ascending=ascending)
            
            # 데이터 표시
            st.dataframe(
                display_df[['회차', '시험과목', '이름', '학과', '학년', '총점', '합격여부', '등급(Lv.)']],
                use_container_width=True,
                height=400
            )
            
            # 다운로드 기능
            csv = display_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 필터링된 데이터 다운로드 (CSV)",
                data=csv,
                file_name=f"pcc_filtered_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        # 탭 6: 성장 추이 분석
        with tab6:
            st.header("📈 성장 추이 분석")
            
            # 1. 전체 성적 추이
            st.subheader("📊 전체 성적 추이")
            
            # 회차별 평균 점수 추이
            round_trend = filtered_df.groupby('회차').agg({
                '총점': ['mean', 'std'],
                '합격여부_binary': 'mean'
            }).reset_index()
            round_trend.columns = ['회차', '평균점수', '표준편차', '합격률']
            round_trend['합격률'] = round_trend['합격률'] * 100
            
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_trend.add_trace(
                go.Scatter(
                    x=round_trend['회차'],
                    y=round_trend['평균점수'],
                    mode='lines+markers+text',
                    name='평균점수',
                    line=dict(color='blue', width=3),
                    text=round_trend['평균점수'].round(1),
                    textposition='top center'
                ),
                secondary_y=False
            )
            
            fig_trend.add_trace(
                go.Scatter(
                    x=round_trend['회차'],
                    y=round_trend['합격률'],
                    mode='lines+markers+text',
                    name='합격률(%)',
                    line=dict(color='green', width=3),
                    text=round_trend['합격률'].round(1).astype(str) + '%',
                    textposition='bottom center'
                ),
                secondary_y=True
            )
            
            fig_trend.update_layout(
                title_text="회차별 평균점수 및 합격률 추이",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            fig_trend.update_xaxes(title_text="회차")
            fig_trend.update_yaxes(title_text="평균점수", secondary_y=False)
            fig_trend.update_yaxes(title_text="합격률(%)", secondary_y=True)
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 2. 재응시 학생 분석
            st.subheader("🔄 재응시 학생 분석")
            
            # 재응시 학생 식별
            retake_students = filtered_df.groupby(['이름', '학번']).filter(lambda x: len(x) > 1)
            
            if not retake_students.empty:
                # 재응시 학생들의 점수 변화
                student_progress = retake_students.groupby(['이름', '학번']).agg({
                    '총점': ['first', 'last', 'mean'],
                    '회차': ['first', 'last']
                }).reset_index()
                
                student_progress.columns = ['이름', '학번', '첫시험점수', '최근시험점수', '평균점수', '첫시험회차', '최근시험회차']
                student_progress['점수향상도'] = student_progress['최근시험점수'] - student_progress['첫시험점수']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 점수 향상도 분포
                    fig_improvement = go.Figure()
                    
                    fig_improvement.add_trace(go.Histogram(
                        x=student_progress['점수향상도'],
                        nbinsx=20,
                        name='점수 향상도 분포'
                    ))
                    
                    fig_improvement.update_layout(
                        title_text="재응시 학생 점수 향상도 분포",
                        xaxis_title="점수 향상도",
                        yaxis_title="학생 수"
                    )
                    
                    st.plotly_chart(fig_improvement, use_container_width=True)
                
                with col2:
                    # 향상도 통계
                    improvement_stats = {
                        '평균 향상도': student_progress['점수향상도'].mean(),
                        '최대 향상도': student_progress['점수향상도'].max(),
                        '최소 향상도': student_progress['점수향상도'].min(),
                        '향상도 표준편차': student_progress['점수향상도'].std(),
                        '향상한 학생 비율': (student_progress['점수향상도'] > 0).mean() * 100
                    }
                    
                    for key, value in improvement_stats.items():
                        st.metric(key, f"{value:.1f}")
                
                # 상세 통계
                st.subheader("📋 재응시 학생 상세 통계")
                st.dataframe(
                    student_progress.sort_values('점수향상도', ascending=False),
                    use_container_width=True
                )
            else:
                st.info("재응시 학생 데이터가 없습니다.")
            
            # 3. 학년별 성적 추이
            st.subheader("🎓 학년별 성적 추이")
            
            # 학년-회차별 통계
            grade_round_stats = filtered_df.groupby(['학년', '회차']).agg({
                '총점': 'mean',
                '합격여부_binary': 'mean'
            }).reset_index()
            
            # 학년별 평균점수 추이
            fig_grade_trend = go.Figure()
            
            for grade in sorted(grade_round_stats['학년'].unique()):
                grade_data = grade_round_stats[grade_round_stats['학년'] == grade]
                fig_grade_trend.add_trace(go.Scatter(
                    x=grade_data['회차'],
                    y=grade_data['총점'],
                    mode='lines+markers+text',
                    name=f'{grade}학년',
                    text=grade_data['총점'].round(1),
                    textposition='top center'
                ))
            
            fig_grade_trend.update_layout(
                title_text="학년별 평균점수 추이",
                xaxis_title="회차",
                yaxis_title="평균점수",
                showlegend=True
            )
            
            st.plotly_chart(fig_grade_trend, use_container_width=True)
            
            # 학년별 상세 통계
            st.subheader("📊 학년별 상세 통계")
            grade_stats = filtered_df.groupby('학년').agg({
                '총점': ['mean', 'std', 'min', 'max'],
                '합격여부_binary': 'mean'
            }).round(2)
            grade_stats.columns = ['평균점수', '표준편차', '최저점수', '최고점수', '합격률']
            grade_stats['합격률'] = (grade_stats['합격률'] * 100).round(1).astype(str) + '%'
            st.dataframe(grade_stats, use_container_width=True)
    else:
        # 일반 사용자용 성장 추이 분석 탭
        with tab4:
            st.header("📈 성장 추이 분석")
            
            # 1. 전체 성적 추이
            st.subheader("📊 전체 성적 추이")
            
            # 회차별 평균 점수 추이
            round_trend = filtered_df.groupby('회차').agg({
                '총점': ['mean', 'std'],
                '합격여부_binary': 'mean'
            }).reset_index()
            round_trend.columns = ['회차', '평균점수', '표준편차', '합격률']
            round_trend['합격률'] = round_trend['합격률'] * 100
            
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_trend.add_trace(
                go.Scatter(
                    x=round_trend['회차'],
                    y=round_trend['평균점수'],
                    mode='lines+markers+text',
                    name='평균점수',
                    line=dict(color='blue', width=3),
                    text=round_trend['평균점수'].round(1),
                    textposition='top center'
                ),
                secondary_y=False
            )
            
            fig_trend.add_trace(
                go.Scatter(
                    x=round_trend['회차'],
                    y=round_trend['합격률'],
                    mode='lines+markers+text',
                    name='합격률(%)',
                    line=dict(color='green', width=3),
                    text=round_trend['합격률'].round(1).astype(str) + '%',
                    textposition='bottom center'
                ),
                secondary_y=True
            )
            
            fig_trend.update_layout(
                title_text="회차별 평균점수 및 합격률 추이",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            fig_trend.update_xaxes(title_text="회차")
            fig_trend.update_yaxes(title_text="평균점수", secondary_y=False)
            fig_trend.update_yaxes(title_text="합격률(%)", secondary_y=True)
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 2. 재응시 학생 분석
            st.subheader("🔄 재응시 학생 분석")
            
            # 재응시 학생 식별
            retake_students = filtered_df.groupby(['이름', '학번']).filter(lambda x: len(x) > 1)
            
            if not retake_students.empty:
                # 재응시 학생들의 점수 변화
                student_progress = retake_students.groupby(['이름', '학번']).agg({
                    '총점': ['first', 'last', 'mean'],
                    '회차': ['first', 'last']
                }).reset_index()
                
                student_progress.columns = ['이름', '학번', '첫시험점수', '최근시험점수', '평균점수', '첫시험회차', '최근시험회차']
                student_progress['점수향상도'] = student_progress['최근시험점수'] - student_progress['첫시험점수']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 점수 향상도 분포
                    fig_improvement = go.Figure()
                    
                    fig_improvement.add_trace(go.Histogram(
                        x=student_progress['점수향상도'],
                        nbinsx=20,
                        name='점수 향상도 분포'
                    ))
                    
                    fig_improvement.update_layout(
                        title_text="재응시 학생 점수 향상도 분포",
                        xaxis_title="점수 향상도",
                        yaxis_title="학생 수"
                    )
                    
                    st.plotly_chart(fig_improvement, use_container_width=True)
                
                with col2:
                    # 향상도 통계
                    improvement_stats = {
                        '평균 향상도': student_progress['점수향상도'].mean(),
                        '최대 향상도': student_progress['점수향상도'].max(),
                        '최소 향상도': student_progress['점수향상도'].min(),
                        '향상도 표준편차': student_progress['점수향상도'].std(),
                        '향상한 학생 비율': (student_progress['점수향상도'] > 0).mean() * 100
                    }
                    
                    for key, value in improvement_stats.items():
                        st.metric(key, f"{value:.1f}")
                
                # 상세 통계
                st.subheader("📋 재응시 학생 상세 통계")
                st.dataframe(
                    student_progress.sort_values('점수향상도', ascending=False),
                    use_container_width=True
                )
            else:
                st.info("재응시 학생 데이터가 없습니다.")
            
            # 3. 학년별 성적 추이
            st.subheader("🎓 학년별 성적 추이")
            
            # 학년-회차별 통계
            grade_round_stats = filtered_df.groupby(['학년', '회차']).agg({
                '총점': 'mean',
                '합격여부_binary': 'mean'
            }).reset_index()
            
            # 학년별 평균점수 추이
            fig_grade_trend = go.Figure()
            
            for grade in sorted(grade_round_stats['학년'].unique()):
                grade_data = grade_round_stats[grade_round_stats['학년'] == grade]
                fig_grade_trend.add_trace(go.Scatter(
                    x=grade_data['회차'],
                    y=grade_data['총점'],
                    mode='lines+markers+text',
                    name=f'{grade}학년',
                    text=grade_data['총점'].round(1),
                    textposition='top center'
                ))
            
            fig_grade_trend.update_layout(
                title_text="학년별 평균점수 추이",
                xaxis_title="회차",
                yaxis_title="평균점수",
                showlegend=True
            )
            
            st.plotly_chart(fig_grade_trend, use_container_width=True)
            
            # 학년별 상세 통계
            st.subheader("📊 학년별 상세 통계")
            grade_stats = filtered_df.groupby('학년').agg({
                '총점': ['mean', 'std', 'min', 'max'],
                '합격여부_binary': 'mean'
            }).round(2)
            grade_stats.columns = ['평균점수', '표준편차', '최저점수', '최고점수', '합격률']
            grade_stats['합격률'] = (grade_stats['합격률'] * 100).round(1).astype(str) + '%'
            st.dataframe(grade_stats, use_container_width=True)

if __name__ == "__main__":
    main() 
