from github import Github
from pprint import pprint
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import json
from tqdm.notebook import tqdm

def get_repo_dict(repo):
    return {"Full name": repo.full_name,
            "Description": repo.description,
            "Date created": repo.created_at,
            "Date of last push": repo.pushed_at,
            "Home Page": repo.homepage,
            "Language": repo.language,
            "Number of forks": repo.forks,
            "Number of stars": repo.stargazers_count,
            "Topics": repo.get_topics(),
            # "Labels": [i._rawData for i in repo.get_labels()],
            # "Contributors": [i._rawData for i in repo.get_contributors()],
            "Contributors Count": repo.get_contributors().totalCount,
            #"Subscribers": [i._rawData for i in repo.get_subscribers()],
            "Subscribers Count": repo.get_subscribers().totalCount,
            #"Watchers": [i._rawData for i in repo.get_watchers()],
            "Watchers Count": repo.get_watchers().totalCount            
           }

g = Github()

topic = st.text_input('Topic')

if(len(topic) > 0):

    all_repo = g.search_repositories(f'topic:{topic}')
    st.write('Total repo count with this topic:', all_repo.totalCount)
    print(all_repo.totalCount)

    topicCountLimit = st.sidebar.slider("Select # of top repos to show:", 0, all_repo.totalCount, all_repo.totalCount%10, 1)
    st.write('Top repo count with this topic:', topicCountLimit)
    print(topicCountLimit)

    progress_bar = st.sidebar.progress(0)
    frame_text = st.sidebar.empty()

    showContributors = st.sidebar.checkbox('Show Contributors')
    showWatchers = st.sidebar.checkbox('Show Watchers')
    showSubscribers = st.sidebar.checkbox('Show Subscribers')

    top_repo = []
    for i, repo in enumerate(all_repo):
        top_repo.append(repo)
        if i+1 == topicCountLimit:
            break

    repo_list = []
    for i, repo in enumerate(top_repo):
        repo_list.append(get_repo_dict(repo))
        if i==0 and topicCountLimit-1==0: j=100
        else: j = (i*100)//(topicCountLimit-1)
        progress_bar.progress(j)
        frame_text.text("Progress %i/100" % (j))

    with open(f'{topic}_top_{topicCountLimit}.json', 'w', encoding='utf-8') as f:
        json.dump(repo_list, f, ensure_ascii=False, indent=4, default=str)  
    repos_df = pd.DataFrame(repo_list)
    print("hello")
    
    from collections import Counter

    topics_list = [i['Topics'] for i in repo_list]
    topics_list_flatten = [item for sublist in topics_list for item in sublist]
    topics_counter = Counter(topics_list_flatten)
    topics_counter = Counter(el for el in topics_counter.elements())
    topics_counter_dict={}
    users_counter_dict={}
    nodes= []
    edges = []
    for k,v in topics_counter.most_common(5):
        node = {"Id": k,
                "Size": v*1000,
                "Type": "topic",
                "Label": k
                }
        nodes.append(node)
        topics_counter_dict[k] = v

    if showContributors or showSubscribers or showWatchers:
        users_list = []

        if showContributors:
            contributorsDict = {}
            for i,repo in enumerate(top_repo):
                contributorsDict[repo.full_name] = [i._rawData['login'] for i in repo.get_contributors()]  
            with open(f'{topic}_contributorsList.json', 'w', encoding='utf-8') as f:
                json.dump(contributorsDict, f, ensure_ascii=False, indent=4, default=str) 
            for k,v in contributorsDict.items():
                users_list.append(v)
        
        if showWatchers:
            watchersDict = {}
            for i,repo in enumerate(top_repo):
                watchersDict[repo.full_name] = [i._rawData['login'] for i in repo.get_watchers()]
            with open(f'{topic}_watchersList.json', 'w', encoding='utf-8') as f:
                json.dump(watchersDict, f, ensure_ascii=False, indent=4, default=str)
            for k,v in contributorsDict.items():
                users_list.append(v)

        if showSubscribers:
            subscribersDict = {}
            for i,repo in enumerate(top_repo):
                subscribersDict[repo.full_name] = [i._rawData['login'] for i in repo.get_subscribers()]
            with open(f'{topic}_subscribersList.json', 'w', encoding='utf-8') as f:
                json.dump(subscribersDict, f, ensure_ascii=False, indent=4, default=str)  
            for k,v in contributorsDict.items():
                users_list.append(v)
        
            
        users_list_flatten = [item for sublist in users_list for item in sublist]
        users_counter = Counter(users_list_flatten)
        users_counter = Counter(el for el in users_counter.elements())
        # print(users_counter)
        for k,v in users_counter.most_common(10):
            node = {"Id": k,
                    "Size": v*1000,
                    "Type": "user",
                    "Label": k
                    }
            nodes.append(node)
            users_counter_dict[k] = v
    
    print(len(nodes))
    print(topics_counter_dict)

    for record in repo_list:
        node = {"Id": record['Full name'],
                "Size": record['Number of stars'],
                "Type": "repo",
                "Label": record['Full name']
                }
        nodes.append(node)
        # print(type(topics_counter.most_common(5)))
        for topic in record['Topics']:
            if topic in topics_counter_dict:
                edge = {"Source": record['Full name'],
                        "Target": topic,
                        "Type": "repo-topic"}
                edges.append(edge)
                
        if showContributors:
            repo_contributors_list = contributorsDict[record['Full name']]
            for contributor in repo_contributors_list:
                if contributor in users_counter_dict:
                    edge = {"Source": record['Full name'],
                        "Target": contributor,
                        "Type": "repo-contributors"}
                    edges.append(edge)
        if showWatchers:
            repo_watchers_list = watchersDict[record['Full name']]
            for watcher in repo_watchers_list:
                if watcher in users_counter_dict:
                    edge = {"Source": record['Full name'],
                        "Target": watcher,
                        "Type": "repo-watchers"}
                    edges.append(edge)
        if showSubscribers:
            repo_subscribers_list = subscribersDict[record['Full name']]
            for subscriber in repo_subscribers_list:
                if subscriber in users_counter_dict:
                    edge = {"Source": record['Full name'],
                        "Target": subscriber,
                        "Type": "repo-subscribers"}
                    edges.append(edge)

    print(len(nodes))
    print(len(edges))


    from pyvis.network import Network
    edges_df = pd.DataFrame(edges)
    print(edges_df)
    print(topics_counter_dict)
    print(users_counter_dict)

    edges_df_repo_topic = pd.DataFrame()
    if not edges_df.empty:
        edges_df_repo_topic = edges_df[edges_df['Type'] == 'repo-topic'] # getting topics related to Leet and Python
        if not edges_df_repo_topic.empty:
            edges_df_repo_topic['Source_Weight'] = edges_df_repo_topic.apply(lambda row: repos_df[repos_df['Full name']==row.Source]["Number of stars"].item(), axis=1)
            edges_df_repo_topic['Target_Weight'] = edges_df_repo_topic.apply(lambda row: topics_counter_dict[row.Target], axis=1)

    edges_df_repo_contributors = pd.DataFrame()
    if showContributors:
        edges_df_repo_contributors = edges_df[edges_df['Type'] == 'repo-contributors']
        if not edges_df_repo_contributors.empty:
            edges_df_repo_contributors['Source_Weight'] = edges_df_repo_contributors.apply(lambda row: repos_df[repos_df['Full name']==row.Source]["Number of stars"].item()%10, axis=1)
            edges_df_repo_contributors['Target_Weight'] = edges_df_repo_contributors.apply(lambda row: users_counter.get(row.Target)%10, axis=1)
    
    edges_df_repo_watchers = pd.DataFrame()
    if showWatchers:
        edges_df_repo_watchers = edges_df[edges_df['Type'] == 'repo-watchers']
        if not edges_df_repo_watchers.empty:
            edges_df_repo_watchers['Source_Weight'] = edges_df_repo_watchers.apply(lambda row: repos_df[repos_df['Full name']==row.Source]["Number of stars"].item()%10, axis=1)
            edges_df_repo_watchers['Target_Weight'] = edges_df_repo_watchers.apply(lambda row: users_counter.get(row.Target)%10, axis=1)
    
    edges_df_repo_subscribers = pd.DataFrame()
    if showSubscribers:
        edges_df_repo_subscribers = edges_df[edges_df['Type'] == 'repo-subscribers']
        if not edges_df_repo_subscribers.empty:
            edges_df_repo_subscribers['Source_Weight'] = edges_df_repo_subscribers.apply(lambda row: repos_df[repos_df['Full name']==row.Source]["Number of stars"].item()%10, axis=1)
            edges_df_repo_subscribers['Target_Weight'] = edges_df_repo_subscribers.apply(lambda row: users_counter.get(row.Target)%10, axis=1)

    frames = [edges_df_repo_topic, edges_df_repo_contributors, edges_df_repo_watchers, edges_df_repo_subscribers]
    edges_final_df = pd.concat(frames)
    print(edges_final_df)

    github_net = Network(height='1000px', width='100%', bgcolor='#222222', directed=False, font_color=True, notebook=True)
    github_net.show_buttons(filter_=['physics','selection','renderer','interaction','manipulation'])
    github_net.set_edge_smooth('dynammic')

    github_net.force_atlas_2based(overlap= 0.5)
    github_data = edges_final_df
    if not edges_final_df.empty:
        sources = github_data['Source']
        targets = github_data['Target']
        source_weights = github_data['Source_Weight']
        target_weights = github_data['Target_Weight']
        types = github_data['Type']

        edge_data = zip(sources, targets, source_weights, target_weights, types)
        for e in edge_data:
            src, dst, src_w, dst_w, typ = e
            github_net.add_node(src, src, title=src, size=src_w, group=1)
            if typ == 'repo-topic':
                github_net.add_node(dst, dst, title=dst, size=dst_w, group=2, shape='square', color='yellow')
            else:
                github_net.add_node(dst, dst, title=dst, size=dst_w, group=3, shape='triangle', color='green')
            github_net.add_edge(src, dst)

        neighbor_map = github_net.get_adj_list()

    # add neighbor data to node hover data
    for node in github_net.nodes:
        node['title'] += ' Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
        node['value'] = len(neighbor_map[node['id']])

    # github_net.show('github_repo_topic.html')

    try:
        path = '/tmp'
        github_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Save and read graph as HTML file (locally)
    except:
        path = '/html_files'
        github_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=2000)